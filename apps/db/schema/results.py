schema_results = {
    '$jsonSchema': {
        'bsonType': 'object',
        'additionalProperties': False,
        'required': ['status', 'created_at', 'expired_at'],
        'properties': {
            '_id': {
                'bsonType': 'objectId',
            },
            "name":{
                'bsonType': 'string',
            },
            'status': {
                'bsonType': 'string',
            },
            'result': {
                'oneOf': [
                    {
                        'bsonType': 'array',
                        'items': {
                            'bsonType': 'array',
                            'items': {
                                'bsonType': ['string', 'int', 'double']
                            }
                        }
                    },
                    {
                        'bsonType': 'object',
                        'additionalProperties': {
                            'bsonType': 'string'
                        }
                    }
                ]
            },
            'expired_at': {"bsonType": 'date'},
            'created_at': {"bsonType": 'date'},
        }
    }
}