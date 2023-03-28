schema_files = {
    '$jsonSchema': {
        'bsonType': 'object',
        'additionalProperties': False,
        'required': ['file_name', 'file', 'created_at', 'expired_at'],
        'properties': {
            '_id': {
                'bsonType': 'objectId',
            },
            'file_name': {
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