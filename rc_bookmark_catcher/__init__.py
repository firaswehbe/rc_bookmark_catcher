import os
import click
from flask import Flask, render_template, request, flash, current_app
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='postgresql://localhost/rcbc',
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

    Bootstrap(app)
    db.init_app(app)

    @app.route("/")
    def index():
        projects = [
            {
                'project_id': 1234,
                'project_title': 'Hello World v1'
            },
            {
                'project_id': 3453,
                'project_title': 'Hello COSMOS v2'
            }
        ]
        return render_template('home.html', projects=projects)
    
    @app.cli.command('dropdb')
    def dropdb():
        from rc_bookmark_catcher import models
        click.echo('Dropping Database...')
        db.drop_all()

    @app.cli.command('initdb')
    def initdb():
        from rc_bookmark_catcher import models
        click.echo('Initializing Database...')
        db.create_all()

    return app
