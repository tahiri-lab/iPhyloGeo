schema_files = {
    '$jsonSchema': {
        'bsonType': 'object',
        'additionalProperties': False,
        'required': ['file_name', 'type', 'file', 'created_at', 'expired_at'],
        'properties': {
            '_id': {
                'bsonType': 'objectId',
            },
            'file_name': {
                'bsonType': 'string',
            },
            'type': {
                'bsonType': 'string',
            },
            'file': {
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
            'last_modified_date': {"bsonType": 'date'},
            'expired_at': {"bsonType": 'date'},
            'created_at': {"bsonType": 'date'},
        }
    }
}