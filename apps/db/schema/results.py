schema_results = {
    '$jsonSchema': {
        'bsonType': 'object',
        'additionalProperties': False,
        'required': ['name'],
        'properties': {
            '_id': {
                'bsonType': 'objectId',
            },
            'name': {
                'bsonType': 'string',
                'description' : 'must be a string and is required'
            },
            'created_at': {"bsonType": 'date'},
        }
    }
}