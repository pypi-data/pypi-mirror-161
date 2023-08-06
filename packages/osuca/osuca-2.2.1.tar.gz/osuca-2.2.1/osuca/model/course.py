import json
from json import JSONEncoder


class Encoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Course):
            return {"subject": o.subject, "id": o.id, "name": o.name}
        return json.JSONEncoder.default(self, o)


class Course:
    def __init__(self, label) -> None:
        tokens = label.split('-')
        self.subject = tokens[0].split(' ')[0].strip()
        self.id = tokens[0].split(' ')[1].strip()
        self.name = tokens[1].strip()

    def __str__(self) -> str:
        return self.toJSON()

    def toJSON(self):
        return json.dumps(self, indent=2, cls=Encoder)

    def __key(self):
        return (self.subject, self.id, self.name)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Course):
            return self.__key() == other.__key()
        return NotImplemented

    def __lt__(self, other):
        return self.id < other.id


if __name__ == '__main__':
    c1 = Course('CS 475 - Intro to Parallel Programming')
    c2 = Course('CS 475 - Intro to Parallel Programming')
    c5 = Course('CS 561 - Data Structures')
    c3 = Course('CS 261 - Data Structures')
    c4 = Course('CS 224 - Data Science')
    print(c1)
    print(c2)
    print(c3)

    print(hash(c1))
    print(hash(c2))

    print(c1 == c2)
    print(c1 == c3)
    print(c3 == c4)
    print(c3 < c4)

    s0 = {c1, c1}
    s1 = {c1, c1}
    print(s0 == s1)

    tx = tuple(s0)
    ty = tuple(s1)
    print(tx == ty)

    s2 = {c1, c2}
    s3 = {c2, c1}
    print(s2 == s3)

    t1 = tuple({c1, c2})
    t2 = tuple({c2, c1})
    print(t1 == t2)

    tx = tuple(s1)
    ty = tuple(s2)
    print(tx == ty)

    s4 = {c1, c3}
    s5 = {c3, c1}
    print(s4 == s5)

    tx = tuple(s4)
    ty = tuple(s5)
    print(tx == ty)

    t3 = tuple({c1, c3})
    t4 = tuple({c3, c1})
    print(t3 == t4)

    s6 = {c1, c5}
    s7 = {c1, c4}
    print(s6 == s7)

    t5 = tuple({c1, c5})
    t6 = tuple({c1, c4})
    print(t5 == t6)

    tx = tuple(s6)
    ty = tuple(s7)
    print(tx == ty)

    s = set()
    s.add(c4)
    s.add(c1)
    s.add(c3)
    s.add(c5)
    sorted_list = sorted(list(s), key=lambda x: (x.id, x.subject))
    print(json.dumps(sorted_list, indent=2, cls=Encoder))
    print(json.dumps(c1, indent=2, cls=Encoder))
    print(c1)

    a = []
    a.append(c4)
    a.append(c1)
    a.append(c3)
    a.append(c5)
    print(json.dumps(c1, indent=2, cls=Encoder))
    print(json.dumps(a, indent=2, cls=Encoder))
    print(json.dumps(c1, indent=2, cls=Encoder))
