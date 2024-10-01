INPUT_SCHEMA = {
    "image": {
        'datatype': 'STRING',
        'required': True,
        'shape': [1],
        'example': ["base64_encoded_image_string"]
    },
    "depth": {
        'datatype': 'STRING',
        'required': True,
        'shape': [1],
        'example': ["base64_encoded_depth_string"]
    }
}