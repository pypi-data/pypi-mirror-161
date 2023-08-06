from __future__ import annotations
from typing import Union, List
from gstorm.enums import MutationMode
import pydash as _pd
import gstorm


def create(
    data: Union[gstorm.GraphQLType, List[gstorm.GraphQLType]],
    mode: MutationMode = MutationMode.BATCH
) -> MutationBuilder:
    """Builds instance of MutationBuilder to sync GraphQLType objects created locally with the remote DB.

    Parameters
    ----------
    data : Union[gstorm.GraphQLType, List[gstorm.GraphQLType]]
      GraphQLType instance(s) to create in the DB
    mode : MutationMode, optional
      allows to upload data by different upload mechanisms, by default MutationMode.BATCH

    Returns
    -------
    MutationBuilder
      Instance of MutationBuilder class, responsible of building mutation string and communication with DB.
    """
    return gstorm.MutationBuilder(data=data, mode=mode)


def save_multi_create(
    to_be_published: List[GraphQLType],
    children_list: List[str],
    api_limit: int = 100
):
    '''Gstorm 'create' method with slicing for batch-size-limited API.\n
    E. g.:\n
    plans = [plan1, plan2] # Where plan1 & plant2 are instances of a GraphQL-schema-based class (e. g. BbtPlan)\n
    errors = multi_create(plans, ['program', 'brightBeer', 'tank'])\n
    # Equivalent to:
    gstorm.create(plans).children(['program', 'brightBeer', 'tank']).run()
    # But sliced...
    '''
    # Since each element amounts for len(children_list),
    # the maximum size an upload batch may have is api_limit//to_be_published
    max_batch_size = api_limit if not children_list else api_limit//len(
        children_list)

    # We need a variable to report any errors when posting items.
    response = {'errors': [], 'messages': []}

    chunked = _pd.chunk(to_be_published, max_batch_size)

    # Iterate over the chunked guy:
    for chunk in chunked:

        # Post the batch
        result = create(chunk).children(children_list).run()

        # Errors, if any, are to be reported
        response['errors'].extend([s for s in result['successful'] if not s])
        response['messages'].extend([s for s in result['messages'] if not s])

    # Report errors
    return response


def update():
    raise NotImplementedError('gstorm.update not implemented')


def upsert():
    raise NotImplementedError('gstorm.upsert not implemented')


def delete():
    raise NotImplementedError('gstorm.delete not implemented')
