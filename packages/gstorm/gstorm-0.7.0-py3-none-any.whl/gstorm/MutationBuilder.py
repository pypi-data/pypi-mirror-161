from __future__ import annotations
from typing import get_type_hints, Dict, List, Union, ForwardRef
from dataclasses import dataclass, field
import json
from datetime import datetime
import inflect
from pygqlc import GraphQLClient
import gstorm
from gstorm.enums import QueryType
from gstorm.helpers.str_handling import remove_capital, contains_digits, capitalize
from gstorm.helpers.date_helpers import get_utc_date, get_iso8601_str
from gstorm.helpers.gql import setup_gql
from gstorm.helpers.typing_helpers import is_enum
from gstorm.helpers.gql_schema_helpers import prettify_query
from gstorm.enums import MutationType, MutationMode

'''

# 1. generar mutations
MUT = MutationBuilder(prog)
# 2. Correr mutations
result, errors = gql.mutate(MUT)
# 3. Update de objeto de Planeacion
if errors:
  prog.set_errors(errors)
  prog.set_sync(false)
else:
  prog.set_sync(true)
  prog.id = result.id
if gstorm.validate(prog):
  send_notification('success')
else:
  send_notification('error')

'''


@dataclass
class MutationBuilder():
    data: Union[List[gstorm.GraphQLType], gstorm.GraphQLType] = None
    # _kind: Union[List[gstorm.GraphQLType], gstorm.GraphQLType] = None # ! IMPLICIT FROM DATA
    mode: MutationMode = MutationMode.BATCH
    _mutation: str = ''
    _children: dict = field(default_factory=dict)
    _isChild: bool = False
    _gql: GraphQLClient = field(default_factory=setup_gql)

    def children(self, *args, **kwargs):
        """Appends child objects to mutation, accepts inputs in several formats:
          children(['room', 'inventories']) # ! DEFAULTS TO SAME MUTATION (CREATE, UPDATE)
          children(
            room = MutationType.UNIQUE, # ! MODE, NO CHILDREN IMPLICIT
            inventories = MutationType.CREATE, # ! MODE, NO CHILDREN IMPLICIT
          )
          children({
            'room': MutationType.UNIQUE, # ! MODE, NO CHILDREN IMPLICIT
            'inventories': {
              '__mode': MutationType.CREATE, # ! MODE, CHILDREN EXPLICIT
              'tank': MutationType.UPSERT
            },
          })

        Returns
        -------
        QueryBuilder
          Same instance that called this method for chaining
        """
        if len(args) > 0:
            if type(args[0]) == str:
                self._children = {
                    **self._children,
                    **{args[0]: MutationType.LOCAL}
                }
            elif type(args[0]) == list:
                new_children = {ch: MutationType.LOCAL for ch in args[0]}
                self._children = {
                    **self._children,
                    **new_children
                }
            elif type(args[0]) == dict:
                self._children = {
                    **self._children,
                    **args[0]
                }
        elif kwargs:
            new_children = {ch: _type for ch, _type in kwargs.items()}
            self._children = {**self._children, **kwargs}
        for key in self._children.keys():
            self._children[key]._isChild = True
        return self

    def pretty_compile(self):
        compiled = self.compile()
        if type(compiled) == list:  # sequence of mutations
            return [prettify_query(compiled_item) for compiled_item in compiled]
        else:
            return prettify_query(self.compile())

    def compile(self):
        if type(self.data) == list:
            return self.compile_plural(self.data, self._children)
        else:
            return self.compile_singular(self.data, self._children)

    def compile_plural(self, data, children):

        batch_items = [
            f'create{type(datum).__name__}_{i}: {self.compile_singular(datum, children, batch=True)}'
            for i, datum in enumerate(data)
        ]
        engine = inflect.engine()
        plural_name = engine.plural(remove_capital(type(data[0]).__name__))
        query_name = 'create' + capitalize(plural_name)
        mutation = f'mutation {query_name} {{ ' + " ".join(batch_items) + ' }'

        return mutation

    def compile_singular(self, data, children, batch=False):
        name = f'create{capitalize(type(data).__name__)}'
        if batch:
            _mutation = '$M_NAME $M_PARAMS{ $M_DEF_FIELDS }'
        else:
            _mutation = 'mutation { $M_NAME $M_PARAMS{ $M_DEF_FIELDS } }'
        _m_def_fields = 'successful messages{ field message } result{ $M_FIELDS }'
        fields = [
            k
            for k, hint in get_type_hints(type(data)).items()
            # filter params (only scalar ones)
            if (
                not k.startswith('__')
                and not hint == List[gstorm.GraphQLType]
                and not type(hint) == ForwardRef
            )
        ]
        singular_params = self.compile_singular_params(data)
        child_params = self.compile_child_params(data, children)
        params = singular_params if not child_params else f'{child_params} {singular_params}'
        # compiled result:
        _mutation = _mutation.replace('$M_DEF_FIELDS', _m_def_fields)
        _mutation = _mutation.replace('$M_NAME', name)
        _mutation = _mutation.replace('$M_PARAMS', f'( {params} )')
        _mutation = _mutation.replace('$M_FIELDS', " ".join(fields))
        mutation_singular = _mutation
        # Process list children to include them in the mutation sequence:
        child_plural_mutations = []
        for children_field, _type in children.items():
            if _type == MutationType.CREATE:
                # ! Inject parent into children to include in mutations:
                for child_obj in data[children_field]:
                    # ! Example: Tank.get_object_fields('Room')[0]
                    parent_field = type(child_obj).get_object_fields(
                        type(data).__name__)[0]
                    child_obj[parent_field] = data
                child_plural_mutations.append(self.compile_plural(
                    data[children_field], {parent_field: MutationType.LOCAL}))
        if child_plural_mutations:
            return [mutation_singular, *child_plural_mutations]
        else:
            # ! single mutation, simplest case
            return mutation_singular

    def compile_singular_params(self, data):
        data_type = type(data)
        hints = get_type_hints(data_type)
        params = [
            (k, data[k])
            for k, hint in hints.items()
            # filter params (only scalar ones)
            if (
                not k.startswith('__')
                and not k in ['id', 'insertedAt', 'updatedAt']
                and not hint == List[gstorm.GraphQLType]
                and not type(hint) == ForwardRef
            )
        ]
        return ' '.join([self.gql_param_dumps(k, v) for k, v in params])

    def compile_child_params(self, data, children):
        params = []
        local_children = [
            child
            for child, mtype in children.items()
            if mtype == MutationType.LOCAL
        ]
        for child in local_children:
            child_obj = data[child]
            if not child_obj:
                continue
            # get first non-empty unique identifier:
            _id = next(iter(child_obj.get_unique_identifiers()))
            key = f'{child}{capitalize(_id)}'
            params.append(self.gql_param_dumps(key, child_obj[_id]))
        return ' '.join(params)

    def gql_param_dumps(self, k, v):
        """Converts GraphQL parameter pair (key, value) to it's serialized form
        Examples:
        - {'capacity': 10} -> 'capacity: 10'
        - {'enabled': True} -> 'enabled: true'
        - {'name': 'L101'} -> 'name: "L101"'
        - {'status': 'FINISHED'} -> 'status: FINISHED'

        Parameters
        ----------
        k : param key
            left-hand side id for graphql parameter pair
        v : param value
            right-hand side value for graphql parameter pair
        """
        if type(v) == int:
            return f'{k}: {v}'
        if type(v) == float:
            return f'{k}: {v}'
        if type(v) == str:
            # regular case, this means it's a string, include double quotes
            return f'{k}: "{v}"'
        if type(v) == bool:
            return f'{k}: {["false","true"][v]}'  # short-hand for inline if
        if type(v) == datetime:
            utc_date = get_utc_date(v)
            return f'{k}: "{get_iso8601_str(utc_date)}"'
        if type(v) == dict:
            quote = '"'
            scape = '\\'
            return f'{k}: "{json.dumps(v).replace(quote, scape + quote)}"'
        if is_enum(v):
            return f'{k}: {v.value}'
        if v is None:
            return f'{k}: null'

    def run(self):

        _mutation = self.compile()
        if type(_mutation) == str:
            # ! SINGLE MUTATION
            data, errors = self._gql.mutate(_mutation)
            if type(self.data) == list:
                # ! BATCH MUTATION
                full_response = {'result': [],
                                 'messages': [], 'successful': []}
                for i, item in enumerate(self.data):
                    label = f'create{type(item).__name__}_{i}'
                    # data for this specific item:
                    item_response = data.get(label)
                    # append to full response:
                    full_response['successful'].append(
                        item_response.get('successful', False))
                    full_response['messages'].extend(
                        item_response.get('messages', []))
                    full_response['result'].append(
                        item_response.get('result', {}))
                    item.__errors__ = item_response['messages'] if len(
                        item_response.get('messages', [])) > 0 else []
                    if 'result' in item_response:
                        item.update(item_response['result'])
                        item.__sync__ = True
                    else:
                        item.__errors__.extend(
                            [{'message': 'No data for this item'}])
                return full_response
            else:
                # ! SIMPLE MUTATION
                self.data.__errors__ = errors
                if not errors:
                    # rebuilds object adding data from DB
                    self.data.update(data['result'])
                    self.data.__sync__ = True
                return data
        elif type(_mutation) == list:
            _mutations = _mutation
            # ! SEQUENTIAL MUTATION
            sequence = [self.data]
            sequence.extend([
                self.data[child]
                for child, _type in self._children.items()
                if _type == MutationType.CREATE
            ])
            full_response = {'result': [], 'messages': [], 'successful': []}
            for mutation, seq_obj in zip(_mutations, sequence):
                # ! Run every mutation sequentially
                data, errors = self._gql.mutate(mutation)
                if type(seq_obj) == list:
                    # ! SEQUENCE - BATCH MUTATION ITEM
                    for i, item in enumerate(seq_obj):
                        label = f'create{type(item).__name__}_{i}'
                        # data for this specific item:
                        item_response = data.get(label)
                        # append to full response:
                        full_response['successful'].append(
                            item_response.get('successful', False))
                        full_response['messages'].extend(
                            item_response.get('messages', []))
                        full_response['result'].append(
                            item_response.get('result', {}))
                        item.__errors__ = item_response['messages'] if len(
                            item_response.get('messages', [])) > 0 else []
                        if 'result' in item_response:
                            item.update(item_response['result'])
                            item.__sync__ = True
                        else:
                            item.__errors__.extend(
                                [{'message': 'No data for this item'}])
                else:
                    # ! SEQUENCE - SINGULAR MUTATION ITEM
                    seq_obj.__errors__ = errors
                    if not errors:
                        # rebuilds object adding data from DB
                        seq_obj.update(data['result'])
                        seq_obj.__sync__ = True
            return full_response
        else:
            raise Exception(
                'Compiled mutation should be either a string or a list of strings')
