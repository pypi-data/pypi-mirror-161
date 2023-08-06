### never forget:
`python setup.py sdist bdist_wheel && python -m twine upload dist/* --skip-existing # UPLOAD TO PYPI`

# python-gstorm
Graphql Simple Tiny Object Relational Mapping - Graphql ORM for python

# Current features:

## QUERY
### Aliases
There are several aliases for most Query-building functions, which make queries more concise:
- query
  - q = query, example: `Type.q() # vs Type.query()`
  - qm = query, example: `Type.qm() # vs Type.query()`
- query_one
  - q1 = query_one, example: `Type.q1() # vs Type.query_one()`
  - qs = query_one, example: `Type.qs() # vs Type.query_one()`
- filter
  - fil = filter, example: `Type.q().fil(...) # vs Type.query().filter(...)`
  - after
    - long: `Type.query().filter(after={'attribute': x, 'date': y})`
    - short: `Type.q().after(attr=x, date=y)`
  - before
    - long: `Type.query().filter(before={'attribute': x, 'date': y})`
    - short: `Type.q().before(attr=x, date=y)`
  - isNull
    - long: `Type.query().filter(nullAttribute={'attribute': x, 'isNull': y})`
    - short: `Type.q().isNull(attr=x, value=True)`
    - shorter: `Type.q().isNull(attr=x)` (Defaults to True)
- findBy
  - fb = findBy, example: `Type.q(). # vs Type.query().`
  - find = findBy, example: `Type.q(). # vs Type.query().`
- orderBy
  - ob = orderBy, example: `Type.q(). # vs Type.query().`
  - order = orderBy, example: `Type.q(). # vs Type.query().`
- limit
  - lim = limit, example: `Type.q(). # vs Type.query().`
- offset
  - off = offset, example: `Type.q(). # vs Type.query().`
- children
  - child = children, example: `Type.q(). # vs Type.query().`
  - ch = children, example: `Type.q(). # vs Type.query().`
- get
  - run = get
### Query all
```python
from tests.models import Tank
all_tanks = Tank.query().get() # returns -> List[Tank]
print(all_tanks) # [Tank(id=1,capacity=10),Tank(id=2,capacity=20),...]
```
### Query some
You can concatenate storm methods to manipulate the data and how you want to receive it,
this methods may receive parameters in several ways:
- filter(kwargs):
  - `.filter(name='L1')`
  - `.filter({'name': 'L1'})`
  - `.filter(name='L1').filter(capacity=1250)`
  - `.filter(name='L1', capacity=1250)`
  - `.filter({'name': 'L1', 'capacity': 1250})`
- orderBy(kwarg):
  - Accepted keys = [asc, desc]
  - Accepted values = GraphQLType ModelAttr enums. 
  - `.orderBy(asc=TypeAttrs.ID)`
  - `.orderBy(desc=TypeAttrs.INSERTED_AT)`
- limit(count)
  - `.limit(1)`
```python
from tests.models import Tank
all_tanks = (
  Tank.query()
  .filter(capacity=1250)
).get() # returns -> List[Tank]
print(all_tanks) # [Tank(id=1,capacity=10),Tank(id=3,capacity=10),...]
```
### Query one
```python
from tests.models import Tank
my_tank = Tank.query_one().findBy(id=3).get() # returns -> Tank
print(my_tank) # Tank(id='3', name='R342', type='Reposo', capacity=0, room=None, inventories=[])
```
### Filters
#### per field value (exact match, regex accepted)
```python
from tests.models import Tank
gov_tanks = Tank.query().filter(type='^Gob').get()
rest_tanks = Tank.query().filter(type='^Rep').get()
print(len(gov_tanks))
print(len(rest_tanks))
```
#### Null attribute
```python
from tests.models import Tank
ok_tanks = (
  Tank.query().filter(nullAttribute= { 'attribute': 'CAPACITY', 'isNull': False })
).get()
print(ok_tanks)

# short-hand version
from tests.models import Tank
ok_tanks = Tank.q().isNull(attr='CAPACITY', value=False).get()
print(ok_tanks)

# using null default value:
from tests.models import Tank
bad_tanks = Tank.q().isNull(attr='CAPACITY').get() # value param defaults to True
print(bad_tanks)
```

#### Comparison dates (after, before)
```python
from tests.models import BbtInventory
from datetime import datetime as dt, timedelta as td
from gstorm.helpers.date_helpers import get_iso8601_str
today = get_iso8601_str(dt.now() - td(days=1))
yesterday = get_iso8601_str(dt.now() - td(days=2))
today_inventories = (
  BbtInventory.query()
    .filter(after={
      'attribute': 'INSERTED_AT',
      'date': "2020-02-27T23:01:44Z" # or: 'date': dt.now() - td(days=1)
    })
).get()
print(today_inventories)

# Short-hand version
today_inventories = (
  BbtInventory.query()
    .after(attr='INSERTED_AT', date="2020-02-27T23:01:44Z") # or: 'date': dt.now() - td(days=1)
).get()
print(today_inventories)

# Short-hand version
yesterday_inventories = (
  BbtInventory.query()
    .after(attr='INSERTED_AT', date=yesterday)
    .before(attr='INSERTED_AT', date=today)
).get()
print(yesterday_inventories)
```
### Ordering
#### Asc, Desc, per field
```python
from tests.models import BbtInventory
latest_inventories = BbtInventory.query().orderBy(desc=BbtInventoryAttrs.ID).limit(5).get()
print(latest_inventories)
smallest_inventories = BbtInventory.query().orderBy(asc=BbtInventoryAttrs.VOLUME).limit(5).get()
print(smallest_inventories)
```
### Limit
```python
from tests.models import BottlingLine
first_10_lines = BottlingLine.query().limit(10).get()
print(first_10_lines)
```
### Nested Queries
```python
from tests.models import BottlingOrder
# We want to include the sub-attributes:
guid = 'abc123'
orders = BottlingOrder.query()._with({
  'line': Line.query(),
  'plans': BottlingPlan.query().orderBy(asc=BottlingPlanAttrs.ID),
  'brightBeer': BrightBeer.query().filter(groupGuid=guid))
}).
print(orders[0])
# >> BottlingOrder(id=1, name='123', line=Line(name='LINEA001'), ...)
```
### Pagination (API NOT FINAL)
#### iterable
```python
from tests.models import Datum
order = {'desc': 'ID'}
for datum_page in Datum.limit(100).offset(0).orderBy(asc=DatumAttrs.ORDER).paginate():
  for datum in datum_page:
    print(datum) # type: Datum(id=x,value=y)
```
#### Comparison numerical (>, >=, <, <=...)
NOT WORKING IN VALIOT-APP

# MUTATION
## Create
```python
from tests.models import Tank
tank = Tank.load(csv='tanks.csv').limit(1).get() # load from any source
response = storm.create(tank) # GraphqlType object
```
## Update
```python
from tests.models import Tank
[gov_tank] = Tank.query().filter(name='L').limit(1).get()
# process data...
# ...
response = storm.update(gov_tank).apply() # GraphqlType object
```
## Upsert
```python
from tests.models import Tank
[gov_tank] = Tank.load(csv='tanks.csv').limit(1).get() # load from any source
response = storm.upsert(gov_tank).apply() # GraphqlType object
if not response.successful:
  print(response.messages)
# everything ok, do other stuff...
print(gov_tank) # has updated data (New ID, etc)
```
## Single mutation
**See above examples**
## Multiple mutation
### Sequential
```python
from tests.models import Tank
gov_tanks = Tank.load(csv='tanks.csv').get() # load from any source
# ! OPTION 1: one by one
for tank in gov_tanks:
  response = storm.upsert(tank).apply() # GraphqlType object
  print(tank) # has updated data (New ID, etc)
# ! OPTION 2: All handled by storm:
response = storm.upsert(gov_tanks).apply()
# response type -> List[GraphqlMutationResponse]
```
### Batch (Multiple mutations in single Mutation tag)
```python
from tests.models import Tank
from storm import UploadMode as mode
gov_tanks = Tank.load(csv='tanks.csv') # load from any source
response = storm.upsert(gov_tanks).mode(mode.BATCH).apply()
# default:
# response = storm.upsert(gov_tanks, mode=mode.SEQUENTIAL)
```
### Nested mutation
**API WIP**:
```python
from tests.models import BbtProgram, BbtPlan
from storm import UploadMode as mode
# algorithm runs...
program = BbtProgram() # New with defaults
for plan in algorithm_plans:
  program.plans.append(BbtPlan(**plan))
# OPTION 1:
response = storm.create(program)
  .nested({
    'plans': Plan.create()
  }).apply()
# OPTION 2:
attrs = ['plans']
response = storm.create(program, nested=attrs)
```

### Parallel/Batch (Multiple mutations multi-threaded, each mutation may be batched)
NOT PRIORITY
# SUBSCRIPTION
NOT PRIORITY

## COMPARISON
```
# # ! old way [No additional libraries]:
# import requests
# import json
# @dataclass
# class Line():
#   id: str
#   name: str
#   speed: float

# LINE = '''
#   query getLine($name: String!){
#     line(findBy:{ name: $name }){
#       id
#       name
#       speed
#     }
#   }
# '''
# url = 'https://test.valiot.app/'
# content = {
#   'query': LINE,
#   'variables': {'name': 'LINEA001'}
# }
# response = requests.post(url, json=content)
# line_data = json.loads(str(response.content))
# line = Line(**line_data)
# line.name # * >> LINEA001
# # ! current way [pygqlc]:
# gql = GraphQLClient()
# @dataclass
# class Line():
#   id: str
#   name: str
#   speed: float

# LINE = '''
#   query getLine($name: String!){
#     line(findBy:{ name: $name }){
#       id
#       name
#       speed
#     }
#   }
# '''
# line_data, _ = gql.query_one(LINE, {'name': 'LINEA001'})
# line = Line(**line_data)
# line.name # * >> LINEA001

# # * New way (TBD):
# gql = GraphQLClient()
# orm = GStorm(client=gql, schema=SCHEMA_PATH)
# Line = orm.getType('Line')
# line = Line.find_one({'name': 'LINEA001'})
# line.name # * >> LINEA001
```
