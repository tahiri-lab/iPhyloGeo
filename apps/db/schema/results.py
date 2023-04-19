schema_results = {
    '$jsonSchema': {
        'bsonType': 'object',
        'additionalProperties': False,
        'required': ['status', 'created_at', 'expired_at'],
        'properties': {
            '_id': {
                'bsonType': 'objectId',
            },
            "name": {
                'bsonType': 'string',
            },
            'status': {
                'bsonType': 'string',
            },
            'climatic_files_id': {
                'bsonType': 'objectId',
            },
            'genetic_files_id': {
                'bsonType': 'objectId',
            },
            'climatic_params': {
                'bsonType': 'object',
                'required': ['names'],
                'properties': {
                    'names': {
                        'bsonType': 'array',
                        'items': {
                            'bsonType': 'string',
                            'minLength': 1,
                        }
                    }
                }
            },
            'climatic_trees': {
                'bsonType': 'object',
            },
            'genetic_trees': {
                'bsonType': 'object',
            },
            'genetic_params': {
                'bsonType': 'object',
                'required': ['bootstrap_amount'],
                'properties': {
                    'bootstrap_amount': {
                        'bsonType': ['int', 'double'],
                    },
                    'bootstrap_threshold': {
                        'bsonType': ['int', 'double'],
                    },
                    'input_step_size_container': {
                        'bsonType': ['int', 'double'],
                    },
                    'ls_threshold': {
                        'bsonType': ['int', 'double'],
                    },
                    'step_size': {
                        'bsonType': ['int', 'double'],
                    },
                    'window_size': {
                        'bsonType': ['int', 'double'],
                    }
                }
            },
            'msaSet': {
                'bsonType': 'object',
            },
            'output': {
                'bsonType': 'array',
                'items': {
                    'bsonType': 'array',
                    'items': {
                        'bsonType': 'string',
                    }
                }
            },
            'expired_at': {"bsonType": 'date'},
            'created_at': {"bsonType": 'date'},
        }
    }
}
