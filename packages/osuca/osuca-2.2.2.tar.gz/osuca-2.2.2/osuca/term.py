from flask import Blueprint, current_app, jsonify, render_template, request
from werkzeug.exceptions import abort

from osuca.db import get_db
from osuca.model.JSONAdapter import Encoder, JSONAdapter

bp = Blueprint('term', __name__)


@bp.route('/')
@bp.route("/term/", methods=['GET', 'POST'])
def index():
    db = get_db()
    adapter = JSONAdapter(db)

    query_result_json = jsonify(adapter.term_aggregate(sort=True)).get_json()
    selection_label = "All Courses"

    if request.method == 'POST' and request.form['course'] != "All Courses":
        selection_label = request.form['course']
        selection = db.course(selection_label)
        query_result_json = jsonify(
            adapter.course_term_aggregate(selection, sort=True)).get_json()

    current_app.json_encoder = Encoder
    return render_template('term.html',
                           selection_label=selection_label,
                           course=sorted(db.course()),
                           term_json=jsonify(
                               adapter.term(sort=True)).get_json(),
                           term=sorted(db.term()),
                           query_result_json=query_result_json)
