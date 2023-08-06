from enum import Enum


class QueryType(Enum):
    PLURAL = 'PLURAL'
    SINGULAR = 'SINGULAR'


class MutationType(Enum):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    UPSERT = 'UPSERT'
    DELETE = 'DELETE'
    LOCAL = 'LOCAL'  # assume local object exists in DB


'''
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

1. CreateProgram
2. Link program.id to every plan
3. CreateDemand (with prev. program.id)
4. CreateOrders
  4.1 Create plans with related order.id
'''


class MutationMode(Enum):
    BATCH = 'BATCH'
    NESTED = 'NESTED'
