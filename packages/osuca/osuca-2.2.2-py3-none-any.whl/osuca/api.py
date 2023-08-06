from flask import current_app, g, jsonify
from flask_restful import Api, Resource

from osuca.db import get_db
from osuca.model.JSONAdapter import Encoder
from osuca.model.JSONAdapter import JSONAdapter as Adapter


def init_app():
    add_resources()


def get_api():
    if 'api' not in g:
        g.api = Api(current_app)
    return g.api


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Course(Resource):
    def get(self):
        return jsonify(Adapter(get_db()).course())


class CourseQuarterAggregate(Resource):
    def get(self):
        return jsonify(Adapter(get_db()).course_quarter_aggregate())


class CourseYearAggregate(Resource):
    def get(self):
        return jsonify(Adapter(get_db()).course_year_aggregate())


def add_resources():
    current_app.json_encoder = Encoder
    get_api().add_resource(HelloWorld, '/restful-hello')
    get_api().add_resource(Course, '/courses')
    get_api().add_resource(CourseQuarterAggregate, '/course-quarter-aggregates')
    get_api().add_resource(CourseYearAggregate, '/course-year-aggregates')
