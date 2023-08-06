import json
from enum import Enum
from json import JSONEncoder


class Encoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Arity):
            return o.lookup()
        return json.JSONEncoder.default(self, o)


class Arity(Enum):
    SOLO = 1
    DUO = 2
    TRIO = 3

    def lookup(self):
        dict = {
            Arity.SOLO: 'Solo',
            Arity.DUO: 'Duo',
            Arity.TRIO: 'Trio',
        }
        return dict[self]

    def __str__(self):
        return self.toJSON()

    def toJSON(self):
        return json.dumps(self, indent=2, cls=Encoder)

    def __lt__(self, other):
        return self.value < other.value
