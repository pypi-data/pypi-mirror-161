from flask import Blueprint, render_template, request, current_app

from osuca.db import get_db

bp = Blueprint('combination', __name__)


@bp.route("/combination/<key>/<reverse>", methods=['GET', 'POST'])
def combination(key, reverse):
    db = get_db()

    query_result = db.course_combination_aggregate()
    selection_label = "All Courses"
    if request.method == 'POST' and request.form['course'] != "All Courses":
        selection_label = request.form['course']
        selection = db.course(selection_label)
        query_result = db.course_combination_aggregate(selection)

    def course(cca): return cca[0][0]
    def count(cca): return cca[1].count
    def mean(cca): return cca[1].mean
    dispatcher = {'course': course, 'count': count, 'mean': mean}
    row_limit = None
    if 'ROW_LIMIT' in current_app.config:
      row_limit = current_app.config['ROW_LIMIT']

    return render_template("combination.html",
                           selection_label=selection_label,
                           course=sorted(db.course()),
                           row_limit=row_limit,
                           query_result=sorted(query_result,
                                               key=dispatcher[key],
                                               reverse=(reverse == 'True')))
