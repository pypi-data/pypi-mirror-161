import os
import sys
from flask import Flask
from flask_cors import CORS

def create_app(test_config=None):
    # Create the app.
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    print("Creating OSU Course Analytics Application: %s" % app.name)
    print("Instance path: %s" % app.instance_path)
    print("System prefix: %s" % sys.prefix)

    # Set some default configuration that the app will use.
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing.
        # If file is not found, we will carry on with default configuration.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists. In a distributed environment, this
    # will be $PREFIX/var/myapp-instance.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # Read environment variables beginning with 'OSUCA', '_' gets dropped.
    app.config.from_prefixed_env('OSUCA')
    data_source = None
    if 'DATA_SOURCE' in app.config:
        data_source = app.config['DATA_SOURCE']

    # Let's initiate the model, treating it as a db that we can query later.
    from . import db
    db.init_app(data_source)

    from . import term
    app.register_blueprint(term.bp)
    # associate the endpoint name 'index' with the / url so that
    # url_for('index') or url_for('term.index') will both work, generating the
    # same / URL either way.
    app.add_url_rule('/', endpoint='index')

    from . import arity
    app.register_blueprint(arity.bp)

    from . import combination
    app.register_blueprint(combination.bp)

    from . import summary 
    app.register_blueprint(summary.bp)

    # Use app_context() in a with block, and everything that runs in the block
    # will have access to current_app.
    from . import api
    with app.app_context():
        api.init_app()

    return app
