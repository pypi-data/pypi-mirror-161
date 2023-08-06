from flask import Blueprint, current_app, jsonify, render_template, request
from werkzeug.exceptions import abort

from osuca.db import get_db
from osuca.model.JSONAdapter import Encoder, JSONAdapter

bp = Blueprint('arity', __name__)


@bp.route("/arity/", methods=['GET', 'POST'])
def arity():
    db = get_db()
    adapter = JSONAdapter(db)

    query_result_json = jsonify(adapter.arity_aggregate(sort=True)).get_json()
    selection_label = "All Courses"

    if request.method == 'POST' and request.form['course'] != "All Courses":
        selection_label = request.form['course']
        selection = db.course(selection_label)
        query_result_json = jsonify(
            adapter.course_arity_aggregate(selection, sort=True)).get_json()

    current_app.json_encoder = Encoder
    return render_template("arity.html",
                           selection_label=selection_label,
                           course=sorted(db.course()),
                           arity_json=jsonify(
                               adapter.arity(sort=True)).get_json(),
                           arity=sorted(db.arity()),
                           query_result_json=query_result_json)
