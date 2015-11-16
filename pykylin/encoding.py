from __future__ import absolute_import

from json import JSONEncoder, JSONDecoder, loads
from json.decoder import WHITESPACE

class KylinJSONEncoder(JSONEncoder):

    def default(self, o):
        return super(KylinJSONEncoder, self).default(self, o)

class KylinJSONDecoder(JSONDecoder):

    def decode(self, s, _w=WHITESPACE.match):
        return super(KylinJSONDecoder, self).decode(s)

def decode(s):
    return loads(s, cls=KylinJSONDecoder)
