import json
from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    def __init__(self, ensure_ascii=False):
        super().__init__(ensure_ascii=False)

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)
