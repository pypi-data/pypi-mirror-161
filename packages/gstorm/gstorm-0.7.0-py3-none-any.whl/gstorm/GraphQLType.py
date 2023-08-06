from __future__ import annotations
import pydash as __
from typing import Optional, List, _GenericAlias, get_type_hints, ForwardRef
from datetime import datetime
from gstorm.helpers.gql import setup_gql
from pprint import pprint
import attr
from dataclasses import dataclass, field
from gstorm.QueryBuilder import QueryBuilder
from gstorm.enums import QueryType
from gstorm.BaseGraphQLType import BaseGraphQLType
from gstorm.helpers.date_helpers import get_local_date, iso8601_to_local_date


def nint(value):
    if value is None:
        return None
    elif type(value) == str:
        return int(value)
    elif type(value) == int:
        return value
    else:
        raise Exception(f"Cannot cast {type(value)} to nullable int")


@attr.s
class GraphQLType(BaseGraphQLType):
    '''Base class for Graphql types,
    has one python's dataclass field per graphql type.
    Plus a __type field with the Type's metadata (opt-out, etc)
    '''
    # __metadata__: str = attr.ib(factory=dict) # attr.ib(default={'opt-out': {}}) # ! MAY BE REQUIRED LATER FOR @opt-out, etc
    __sync__: bool = attr.ib(repr=False, default=False)
    __errors__: List[dict] = attr.ib(repr=False, factory=list)
    id: Optional[int] = attr.ib(
        default=None, converter=nint, metadata={'unique': {}, 'type':int, 'model':None})
    insertedAt: datetime = attr.ib(repr=False, factory=lambda: get_local_date(
        datetime.now()), converter=iso8601_to_local_date, metadata={'readonly': True, 'type':datetime, 'model':None})
    updatedAt: datetime = attr.ib(repr=False, factory=lambda: get_local_date(
        datetime.now()), converter=iso8601_to_local_date, metadata={'readonly': True, 'type':datetime, 'model':None})

    def __attrs_post_init__(self):
        """[summary]
        """
        self._public_keys = self.get_public_fields()

    def __getitem__(self, item):
        if type(item) == str:
            return self.__getattribute__(item)
        elif type(item) == int:
            key = self._public_keys[item]
            return key, self.__getattribute__(key)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    @classmethod
    def get_field(cls, name):
        return attr.fields_dict(cls).get(name)

    @classmethod
    def get_fields(cls):
        return attr.fields_dict(cls)

    @classmethod
    def get_public_fields(cls):
        return [key for key in cls.get_fields().keys() if not key.startswith('__')]

    @classmethod
    def get_base_fields(cls):
        list_fields = [
            name
            for name, hint in get_type_hints(cls).items()
            if hint != List[GraphQLType]  # if not type List
            # GraphQL types are forward-referenced
            and not type(hint) == ForwardRef
            and not name.startswith('_')
        ]
        return list_fields

    @classmethod
    def get_list_fields(cls):
        list_fields = [
            name
            for name, hint in get_type_hints(cls).items()
            if hint == List[GraphQLType]  # if not type List
        ]
        return list_fields

    @classmethod
    def get_object_fields(cls, typename=None):
        obj_fields = {
            name: hint
            for name, hint in get_type_hints(cls).items()
            if (
                type(hint) == ForwardRef
                # and hint.__forward_arg__ == typename if typename else True # filters by object type
            )
        }
        if typename:
            obj_fields = {
                name: hint
                for name, hint in obj_fields.items()
                if hint.__forward_arg__ == typename
            }
        return list(obj_fields.keys())

    @classmethod
    def get_unique_fields(cls):
        return [
            name
            for name, field in attr.fields_dict(cls).items()
            if 'unique' in field.metadata
        ]

    @classmethod
    def get_field_types(cls):
        return {k: v for k, v in get_type_hints(cls).items() if not k.startswith('_')}

    @classmethod
    def get_metadata(cls, field_name):
        field = attr.fields_dict(cls)[field_name]
        return field.metadata

    def get_unique_identifiers(self):
        return {
            k: self[k]
            for k in self.get_unique_fields()
            if self[k]
        }

    def create(self):
        pass

    def load(self):
        raise NotImplementedError('Child class should implement load method')

    @classmethod
    def query(cls):
        return QueryBuilder(_kind=cls)

    @classmethod
    def query_one(cls):
        return QueryBuilder(cls, QueryType.SINGULAR)

    def is_sync(self):
        return self.__sync__

    def has_errors(self):
        return len(self.__errors__) > 0

    def get_errors(self):
        return self.__errors__

    def update(self, data):
        # Transforms object with selected data
        fields = self.get_fields().keys()
        for key, value in data.items():
            if key in fields:
                self[key] = value
    # ! method aliases
    # query
    q = query
    qm = query
    qp = query  # query plural
    # query_one
    q1 = query_one
    qs = query_one  # query singular
