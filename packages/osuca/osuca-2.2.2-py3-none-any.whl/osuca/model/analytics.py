import csv
from functools import partial

from osuca.model.course import Course
from osuca.model.quarter import Quarter
from osuca.model.arity import Arity


class Aggregate():
    def __init__(self):
        self.count = 0
        self.sum = 0
        self.mean = None

    def compute(self):
        if self.count != 0:
            self.mean = self.sum / self.count


class Analytics():
    """Contains in-memory structures for analytics."""

    def __init__(self, input):
        print('Initializing analytics.')
        self.evaluation = set()

        reader = csv.reader(input.splitlines(), delimiter=',')
        next(reader)  # skip header

        id = 0
        for row in reader:
            quarter = Quarter(row[5])
            if quarter.invalid():
                print('Rejecting line %d...' % id)
            else:
                id += 1
                term = quarter.term
                year = quarter.year
                if row[11].lower() == 'yes':
                    ca = Course(row[1])
                    cb = Course(row[7])
                    cc = Course(row[12])
                    da = int(row[2])
                    db = int(row[8])
                    dc = int(row[13])
                    trio = frozenset({ca, cb, cc})
                    self.evaluation.add(
                        (id, ca, term, year, da, trio, Arity(Arity.TRIO)))
                    self.evaluation.add(
                        (id, cb, term, year, db, trio, Arity(Arity.TRIO)))
                    self.evaluation.add(
                        (id, cc, term, year, dc, trio, Arity(Arity.TRIO)))
                elif row[6].lower() == 'yes':
                    ca = Course(row[1])
                    cb = Course(row[7])
                    da = int(row[2])
                    db = int(row[8])
                    duo = frozenset({ca, cb})
                    self.evaluation.add(
                        (id, ca, term, year, da, duo, Arity(Arity.DUO)))
                    self.evaluation.add(
                        (id, cb, term, year, db, duo, Arity(Arity.DUO)))
                else:
                    ca = Course(row[1])
                    da = int(row[2])
                    solo = frozenset({ca})
                    self.evaluation.add(
                        (id, ca, term, year, da, solo, Arity(Arity.SOLO)))

        print('response count: %d' % len(self.response()))
        print('evaluation count: %d' % self.evaluation_count())
        print('course count: %d' % len(self.course()))
        print('term count: %d' % len(self.term()))
        print('year count: %d' % len(self.year()))
        print('quarter count: %d' % len(self.quarter()))
        print('course-term count: %d' % len(self.course_term()))
        print('course-year count: %d' % len(self.course_year()))
        print('course-quarter count: %d' % len(self.course_quarter()))
        print('combination count: %d' % len(self.combination()))
        print('solo count: %d' % len(self.solo()))
        print('duo count: %d' % len(self.duo()))
        print('trio count: %d' % len(self.trio()))

    def aggregate(self, o, key=None):
        agg = Aggregate()
        if key is None:
            for e in self.evaluation:
                agg.sum = agg.sum + e[4]
                agg.count += 1
        elif len(key) == 1:
            for e in self.evaluation:
                if e[key[0]] == o:
                    agg.sum = agg.sum + e[4]
                    agg.count += 1
        elif len(key) == 2:
            if key[0] == 2 and key[1] == 3:            # quarter, i.e, term-year
                for e in self.evaluation:
                    if e[2] == o.term and e[3] == o.year:
                        agg.sum = agg.sum + e[4]
                        agg.count += 1
            elif key[0] == 1 and key[1] == 2:          # course-term
                for e in self.evaluation:
                    if e[1] == o[0] and e[2] == o[1]:
                        agg.sum = agg.sum + e[4]
                        agg.count += 1
            elif key[0] == 1 and key[1] == 3:          # course-year
                for e in self.evaluation:
                    if e[1] == o[0] and e[3] == o[1]:
                        agg.sum = agg.sum + e[4]
                        agg.count += 1
            elif key[0] == 1 and key[1] == 5:          # course-combination
                for e in self.evaluation:
                    if e[1] == o[0] and e[5] == o[1]:
                        agg.sum = agg.sum + e[4]
                        agg.count += 1
        elif key[0] == 1 and key[1] == 2 and key[2] == 3:  # course-term-year
            for e in self.evaluation:
                if e[1] == o[0] and e[2] == o[1].term and e[3] == o[1].year:
                    agg.sum = agg.sum + e[4]
                    agg.count += 1

        agg.compute()
        return (o,) + (agg,)

    def evaluation_count(self):
        return len(self.evaluation)

    def response(self):
        """Unary predicate for response."""
        return {e[0] for e in self.evaluation}

    def response_aggregate(self):
        """Unary predicate for representing aggregate response."""
        return set(map(self.aggregate, self.response()))

    def course(self, label=None):
        """Unary predicate for course."""
        if label is None:
            return {e[1] for e in self.evaluation}

        tokens = label.split('-')
        subject = tokens[0].split(' ')[0].strip()
        id = tokens[0].split(' ')[1].strip()
        return {e[1] for e in self.evaluation if e[1].subject == subject and e[1].id == id}

    def course_aggregate(self):
        """Binary predicate for course-aggregate relation."""
        return set(map(partial(self.aggregate, key=(1,)), self.course()))

    def term(self):
        """Unary predicate for term."""
        return {e[2] for e in self.evaluation}

    def term_aggregate(self):
        """Binary predicate for term-aggregate relation."""
        return set(map(partial(self.aggregate, key=(2,)), self.term()))

    def arity(self):
        return {Arity(len(e[5])) for e in self.evaluation}

    def arity_aggregate(self):
        """Binary predicate for arity-aggregate relation."""
        return set(map(partial(self.aggregate, key=(6,)), self.arity()))

    def year(self):
        """Unary predicate for year."""
        return {e[3] for e in self.evaluation}

    def year_aggregate(self):
        """Binary predicate for year-aggregate relation."""
        return set(map(partial(self.aggregate, key=(3,)), self.year()))

    def quarter(self):
        """Unary predicate for quarter."""
        return {Quarter(e[2].lookup() + e[3]) for e in self.evaluation}

    def quarter_aggregate(self):
        """Binary predicate for quarter-aggregate relation."""
        return set(map(partial(self.aggregate, key=(2, 3)), self.quarter()))

    def course_term(self, course=None):
        """Binary predicate for course-term relation.

        Course is taken in Term, e.g., CS 261 is taken in Summer.
        Term has Course, e.g.,  Summer has CS 261. 
        """
        if course is None:
            return {(e[1], e[2]) for e in self.evaluation}
        else:
            return {(e[1], e[2]) for e in self.evaluation if e[1] in course}

    def course_arity(self, course=None):
        """Binary predicate for course-arity relation.

        Course is taken in Term, e.g., CS 261 is taken in Summer.
        Term has Course, e.g.,  Summer has CS 261. 
        """
        if course is None:
            return {(e[1], e[6]) for e in self.evaluation}
        else:
            return {(e[1], e[6]) for e in self.evaluation if e[1] in course}

    def course_arity_aggregate(self, course=None):
        """Ternary predicate for course-arity-aggregate relation."""
        course_arity = self.course_arity(course)
        return set(map(partial(self.aggregate, key=(1, 6)), course_arity))

    def course_term_aggregate(self, course=None):
        """Ternary predicate for course-term-aggregate relation."""
        course_term = self.course_term(course)
        return set(map(partial(self.aggregate, key=(1, 2)), course_term))

    def course_year(self):
        """Binary predicate for course-year relation.

        Course is taken in Year, e.g., CS 261 is taken in Summer.
        Year has Course, e.g.,  2022 has CS 261. 
        """
        return {(e[1], e[3]) for e in self.evaluation}

    def course_year_aggregate(self):
        """Ternary predicate for course-year-aggregate relation."""
        return set(map(partial(self.aggregate, key=(1, 3)), self.course_year()))

    def course_quarter(self):
        """Binary predicate for course-quarter relation.
        """
        return {(e[1], Quarter(e[2].lookup() + e[3])) for e in self.evaluation}

    def course_quarter_aggregate(self):
        """Ternary predicate for course-quarter-aggregate relation."""
        return set(map(partial(self.aggregate, key=(1, 2, 3)), self.course_quarter()))

    def combination(self):
        return {e[5] for e in self.evaluation}

    def solo(self):
        """Combination with a single course.
        """
        return {e[5] for e in self.evaluation if (len(e[5]) == 1)}

    def duo(self):
        """Combination with two courses.
        """
        return {e[5] for e in self.evaluation if (len(e[5]) == 2)}

    def trio(self):
        """Combination with three courses.
        """
        return {e[5] for e in self.evaluation if (len(e[5]) == 3)}

    def course_combination(self, course=None):
        """Binary predicate for course-combination relation.
        """
        if course is None:
            return {(e[1], e[5]) for e in self.evaluation}
        return {(e[1], e[5]) for e in self.evaluation if e[1] in course}

    def course_combination_aggregate(self, course=None):
        """Ternary predicate for course-combination-aggregate relation."""
        if course is None:
            return set(map(partial(self.aggregate, key=(1, 5)), self.course_combination()))
        return set(map(partial(self.aggregate, key=(1, 5)), self.course_combination(course)))
