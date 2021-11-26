from structure.models import ResponseType

import os
print(os.getcwd())

with open('./structure/raw-data/response-type.txt') as f:
    lines = f.readlines()
    response_type_dict = {}
    for line in lines:
        splitted = [e.strip() for e in line.split('|')]
        cleaned = [None if e == 'NULL' else e for e in splitted][1:-1]
        id, parent_type_id, url, method, parameter, base_mime_type = cleaned
        if parent_type_id:
            parent_type = response_type_dict[parent_type_id]
        else:
            parent_type = None
        response_type = ResponseType(
            id=id,
            parent_type=parent_type,
            url=url,
            method=method,
            parameter=parameter,
            base_mime_type=base_mime_type
        )
        response_type.save()
        response_type_dict[id] = response_type

print(response_type_dict)
