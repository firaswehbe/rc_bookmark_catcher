import os
from flask import Flask, render_template, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='postgresql://rcbc@localhost/rcbc',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        LOGGING_LEVEL='DEBUG'
    )

    if test_config is None:
        app.config.from_pyfile('application.cfg', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def index():
        if request.args.get('pid') is None:
            flash("A valid project id is required for this page")
        return render_template('base.html')
    
    Bootstrap(app)
    db.init_app(app)

    return app

