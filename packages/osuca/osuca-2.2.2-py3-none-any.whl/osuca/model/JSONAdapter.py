import json
from json import JSONEncoder

from osuca.model.analytics import Aggregate
from osuca.model.course import Course
from osuca.model.quarter import Term, Quarter
from osuca.model.arity import Arity


class JSONAdapter():
    def __init__(self, analytics):
        self.analytics = analytics

    def response(self, sort=False):
        """Returns json representation for all responses."""
        result = self.analytics.response()
        return sorted(list(result)) if sort else list(result)

    def response_aggregate(self):
        """Returns json representation for aggregate response."""
        # aggregate is the same for all response
        # we get the first tuple and then set the result to the second element
        return list(self.analytics.response_aggregate()).pop()[1]

    def course(self, sort=False):
        """Returns json representation for course predicate."""
        result = self.analytics.course()
        return sorted(list(result)) if sort else list(result)

    def course_aggregate(self, sort=False):
        """Returns json representation for course aggregate predicate."""
        result = [CourseAggregate(ca)
                  for ca in self.analytics.course_aggregate()]
        return sorted(result) if sort else result

    def term(self, sort=False):
        """Returns json representation for term predicate."""
        result = self.analytics.term()
        return sorted(list(result)) if sort else list(result)

    def arity(self, sort=False):
        """Returns json representation for term predicate."""
        result = self.analytics.arity()
        return sorted(list(result)) if sort else list(result)

    def term_aggregate(self, sort=False):
        """Returns json representation for term aggregate predicate."""
        result = [TermAggregate(ta) for ta in self.analytics.term_aggregate()]
        return sorted(result) if sort else result

    def arity_aggregate(self, sort=False):
        """Returns json representation for term aggregate predicate."""
        result = [ArityAggregate(aa)
                  for aa in self.analytics.arity_aggregate()]
        return sorted(result) if sort else result

    def year(self, sort=False):
        """Returns json representation for term predicate."""
        result = self.analytics.year()
        return sorted(list(result)) if sort else list(result)

    def year_aggregate(self, sort=False):
        """Returns json representation for year aggregate predicate."""
        result = [YearAggregate(ya) for ya in self.analytics.year_aggregate()]
        return sorted(result) if sort else result

    def quarter(self, sort=False):
        """Returns json representation for quarter predicate."""
        result = self.analytics.quarter()
        return sorted(list(result)) if sort else list(result)

    def quarter_aggregate(self, sort=False):
        """Returns json representation for quarter aggregate predicate."""
        result = [QuarterAggregate(qa)
                  for qa in self.analytics.quarter_aggregate()]
        return sorted(result) if sort else result

    def course_term(self, sort=False):
        """Returns json representation for course-term relations."""
        result = [CourseTerm(ct) for ct in self.analytics.course_term()]
        return sorted(result) if sort else result

    def course_term_aggregate(self, course=None, sort=False):
        """Returns json representation for course-term aggregate predicate."""
        if course is None:
            result = self.analytics.course_term_aggregate()
        else:
            result = self.analytics.course_term_aggregate(course)
        result = [CourseTermAggregate(cta) for cta in result]
        return sorted(result) if sort else result

    def course_arity_aggregate(self, course=None, sort=False):
        """Returns json representation for course-arity aggregate predicate."""
        if course is None:
            result = self.analytics.course_arity_aggregate()
        else:
            result = self.analytics.course_term_aggregate(course)
        result = [CourseArityAggregate(caa) for caa in result]
        return sorted(result) if sort else result

    def course_year(self, sort=False):
        """Returns json representation for course-year relations."""
        result = [CourseYear(cy) for cy in self.analytics.course_year()]
        result = sorted(result) if sort else result
        return sorted(result) if sort else result

    def course_year_aggregate(self, sort=False):
        """Returns json representation for course-term aggregate predicate."""
        result = self.analytics.course_year_aggregate()
        result = [CourseYearAggregate(cya) for cya in result]
        return sorted(result) if sort else result

    def course_quarter(self, sort=False):
        """Returns json representation for course-quarter relations."""
        result = [CourseQuarter(cq) for cq in self.analytics.course_quarter()]
        return sorted(result) if sort else result

    def course_quarter_aggregate(self, sort=False):
        """Returns json representation for course-term aggregate predicate."""
        result = self.analytics.course_quarter_aggregate()
        result = [CourseQuarterAggregate(cqa) for cqa in result]
        return sorted(result) if sort else result

    def course_combination_aggregate(self, sort=False):
        """Returns json representation for course-combination aggregate predicate."""
        result = self.analytics.course_combination_aggregate()
        result = [CourseCombinationAggregate(cqa) for cqa in result]
        return sorted(result) if sort else result


class Encoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Arity):
            return o.lookup()
        if isinstance(o, Course):
            return {"course": o.__dict__}
        if isinstance(o, Term):
            return o.lookup()
        if isinstance(o, Quarter):
            return {"quarter": o.__dict__}
        if isinstance(o, Aggregate):
            return {"aggregate": o.__dict__}
        if isinstance(o, CourseAggregate):
            return {"course": o.course.__dict__, "aggregate": o.aggregate.__dict__}
        if isinstance(o, ArityAggregate):
            return {"arity": o.arity.lookup(), "aggregate": o.aggregate.__dict__}
        if isinstance(o, TermAggregate):
            return {"term": o.term.lookup(), "aggregate": o.aggregate.__dict__}
        if isinstance(o, YearAggregate):
            return {"year": o.year, "aggregate": o.aggregate.__dict__}
        if isinstance(o, QuarterAggregate):
            return {
                "quarter": {
                    "term": o.quarter.term.lookup(),
                    "year": o.quarter.year
                },
                "aggregate": o.aggregate.__dict__
            }
        if isinstance(o, CourseTerm):
            return {"course": o.course.__dict__, "term": o.term.lookup()}
        if isinstance(o, CourseTermAggregate):
            return {
                "course": o.course.__dict__,
                "term": o.term.lookup(),
                "aggregate": o.aggregate.__dict__
            }
        if isinstance(o, CourseArityAggregate):
            return {
                "course": o.course.__dict__,
                "arity": o.arity.lookup(),
                "aggregate": o.aggregate.__dict__
            }
        if isinstance(o, CourseYear):
            return {"course": o.course.__dict__, "year": o.year}
        if isinstance(o, CourseYearAggregate):
            return {
                "course": o.course.__dict__,
                "year": o.year,
                "aggregate": o.aggregate.__dict__
            }
        if isinstance(o, CourseQuarter):
            return {
                "course": o.course.__dict__,
                "quarter": {
                    "term": o.quarter.term.lookup(),
                    "year": o.quarter.year
                }
            }
        if isinstance(o, CourseQuarterAggregate):
            return {
                "course": o.course,
                "quarter": o.quarter,
                "aggregate": o.aggregate
            }
        if isinstance(o, CourseCombinationAggregate):
            combo = {}
            for count, course in enumerate(o.combination):
                if course != o.course:
                    combo["course-" + str(count)] = (course.__dict__)
            return {
                "course": o.course.__dict__,
                "combination": combo,
                "aggregate": o.aggregate.__dict__
            }
        print(type(o))
        return json.JSONEncoder.default(self, o)


class CourseAggregate():
    def __init__(self, t):
        self.course = t[0]
        self.aggregate = t[1]

    def __lt__(self, other):
        return self.aggregate.mean < other.aggregate.mean


class ArityAggregate():
    def __init__(self, t):
        self.arity = t[0]
        self.aggregate = t[1]

    def __lt__(self, other):
        return self.arity < other.arity


class TermAggregate():
    def __init__(self, t):
        self.term = t[0]
        self.aggregate = t[1]

    def __lt__(self, other):
        return self.term < other.term


class YearAggregate():
    def __init__(self, t):
        self.year = t[0]
        self.aggregate = t[1]

    def __lt__(self, other):
        return self.year < other.year


class QuarterAggregate():
    def __init__(self, t):
        self.quarter = t[0]
        self.aggregate = t[1]

    def __lt__(self, other):
        return self.quarter < other.quarter


class CourseTerm():
    def __init__(self, t):
        self.course = t[0]
        self.term = t[1]

    def __lt__(self, other):
        if self.course < other.course:
            return True
        elif self.course > other.course:
            return False
        else:
            return self.term < other.term


class CourseTermAggregate():
    def __init__(self, t):
        self.course = t[0][0]
        self.term = t[0][1]
        self.aggregate = t[1]

    def __lt__(self, other):
        if self.course < other.course:
            return True
        elif self.course > other.course:
            return False
        else:
            return self.term < other.term


class CourseArity():
    def __init__(self, t):
        self.course = t[0]
        self.arity = t[1]

    def __lt__(self, other):
        if self.course < other.course:
            return True
        elif self.course > other.course:
            return False
        else:
            return self.arity < other.arity


class CourseArityAggregate():
    def __init__(self, t):
        self.course = t[0][0]
        self.arity = t[0][1]
        self.aggregate = t[1]

    def __lt__(self, other):
        if self.course < other.course:
            return True
        elif self.course > other.course:
            return False
        else:
            return self.arity < other.arity


class CourseYear():
    def __init__(self, t):
        self.course = t[0]
        self.year = t[1]

    def __lt__(self, other):
        if self.course < other.course:
            return True
        elif self.course > other.course:
            return False
        else:
            return self.year < other.year


class CourseYearAggregate():
    def __init__(self, t):
        self.course = t[0][0]
        self.year = t[0][1]
        self.aggregate = t[1]

    def __lt__(self, other):
        if self.course < other.course:
            return True
        elif self.course > other.course:
            return False
        else:
            return self.year < other.year


class CourseQuarter():
    def __init__(self, t):
        self.course = t[0]
        self.quarter = t[1]

    def __lt__(self, other):
        if self.course < other.course:
            return True
        elif self.course > other.course:
            return False
        else:
            return self.quarter < other.quarter


class CourseQuarterAggregate():
    def __init__(self, t):
        self.course = t[0][0]
        self.quarter = t[0][1]
        self.aggregate = t[1]

    def __lt__(self, other):
        if self.course < other.course:
            return True
        elif self.course > other.course:
            return False
        else:
            return self.quarter < other.quarter


class CourseCombinationAggregate():
    def __init__(self, t):
        self.course = t[0][0]
        self.combination = t[0][1]
        self.aggregate = t[1]

    def __lt__(self, other):
        if self.course < other.course:
            return True
        elif self.course > other.course:
            return False
        else:
            return self.aggregate.mean < other.aggregate.mean
