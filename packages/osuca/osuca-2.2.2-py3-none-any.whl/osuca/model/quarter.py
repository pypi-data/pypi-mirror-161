import json
from enum import Enum
from json import JSONEncoder


class Encoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Term):
            return o.lookup()
        if isinstance(o, Quarter):
            return {"term": o.term.lookup(), "year": o.year}
        return json.JSONEncoder.default(self, o)


class Term(Enum):
    WINTER = 0
    SPRING = 1
    SUMMER = 2
    FALL = 3

    def lookup(self):
        dict = {
            Term.WINTER: 'Winter',
            Term.SPRING: 'Spring',
            Term.SUMMER: 'Summer',
            Term.FALL: 'Fall'
        }
        return dict[self]

    def __str__(self):
        return self.toJSON()

    def toJSON(self):
        return json.dumps(self, indent=2, cls=Encoder)

    def __lt__(self, other):
        return self.value < other.value


class Quarter:
    def __init__(self, label) -> None:
        year = ''.join(filter(str.isdigit, label))
        year = year[-2:]
        self.year = None
        if len(year) != 0 and int(year) > 14:
            self.year = '20' + year

        term = ''.join(filter(str.isalpha, label)).upper()
        self.term = None
        if 'W' in term:
            self.term = Term.WINTER
        elif 'P' in term:
            self.term = Term.SPRING
        elif 'U' in term:
            self.term = Term.SUMMER
        elif 'F' in term:
            self.term = Term.FALL

    def invalid(self):
        return self.year is None or self.term is None

    def __str__(self):
        return self.toJSON()

    def toJSON(self):
        return json.dumps(self, indent=2, cls=Encoder)

    def __key(self):
        return (self.term, self.year)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Quarter):
            return self.__key() == other.__key()
        return NotImplemented

    def __lt__(self, other):
        if self.year < other.year:
            return True
        elif self.year > other.year:
            return False
        else:
            return self.term < other.term


if __name__ == '__main__':
    q1 = Quarter('f2019')
    q2 = Quarter('w2019')
    q3 = Quarter('u2018')
    q4 = Quarter('p2015')
    q5 = Quarter('u2019')
    q6 = Quarter('p2019')
    print(q1)
    print(q2)
    print(q3)
    print(q4)

    s = {q6, q5, q2, q3, q4, q1}
    sorted_list = sorted(list(s))
    print(json.dumps(sorted_list, indent=2, cls=Encoder))

    t1 = Term.WINTER
    t2 = Term.FALL
    t3 = Term.SPRING
    s = {t1, t2, t3}
    sorted_list = sorted(list(s))
    print(json.dumps(sorted_list, indent=2, cls=Encoder))
    print(json.dumps(t1, indent=2, cls=Encoder))
    print(t1)
