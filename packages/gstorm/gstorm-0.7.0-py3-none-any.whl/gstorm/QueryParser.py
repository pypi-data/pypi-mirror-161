
# ! Referencia para posible pre-procesador de queries

# SOURCE
query = '''
query MyQuery(
  $name: String!
  $capacity: Integer = 1000
){
  gov_tanks: tanks(
    name: $name
    capacity: $capacity
    type: "Gobierno"
  ){
    id
    name
    insertedAt
    location: room {
      id
      name
    }
    inventories (orderBy: { asc: ID } limit: 1) {
      id
      volume
    }
  }
  rooms {
    id
    name
  }
}
'''

# RESULT
parsed_query = {
  '__type': 'Query',
  'label': 'MyQuery',
  'variables': {
    'name': {
      '__type': 'String',
      'required': True,
      'default': None
    },
    'capacity': {
      '__type': 'Integer',
      'required': False,
      'default': 1000
    }
  },
  'operations': [{
    'label': 'gov_tanks',
    'name': 'tanks',
    'params': [
      'name': GraphQLVariable('name')
      'capacity': GraphQLVariable('capacity')
      'type': "Gobierno"
    ],
    'fields': [{
      'label': None,
      'name': 'id',
      'params': [],
      'fields': []
    }, {
      'label': None,
      'name': 'name',
      'params': [],
      'fields': []
    }, {
      'label': None,
      'name': 'insertedAt',
      'params': [],
      'fields': []
    }, {
      'label': 'location',
      'name': 'room',
      'params': [],
      'fields': [{
        'label': None,
        'name': 'id',
        'params': [],
        'fields': []
      }, {
        'label': None,
        'name': 'name',
        'params': [],
        'fields': []
      }]
    }, {
      'label': None,
      'name': 'inventories',
      'params': [
        'orderBy': { 'asc': 'ID' },
        'limit': 1
      ],
      'fields': [{
        'label': None,
        'name': 'id',
        'params': [],
        'fields': []
      }, {
        'label': None,
        'name': 'volume',
        'params': [],
        'fields': []
      }]
    }]
  }, {
    'label': None,
    'name': 'rooms',
    'params': [],
    'fields': [{
      'label': None,
      'name': 'id',
      'params': [],
      'fields': []
    }, {
      'label': None,
      'name': 'name',
      'params': [],
      'fields': []
    }]
  }]
}