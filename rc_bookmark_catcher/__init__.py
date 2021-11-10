import os
import click
from flask import Flask, render_template, request, flash, current_app
from flask import url_for, redirect
from flask_bootstrap import Bootstrap

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='postgresql://localhost/rcbc',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        LOGGING_LEVEL='DEBUG',
        REDCAP_URL='https://redcap.nubic.northwestern.edu/api/'
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

    ##########
    # ROUTES #
    ##########

    @app.route("/")
    def index():
        from rc_bookmark_catcher.models import Project
        myprojects = Project.query.order_by(Project.project_id).all()
        return render_template('home.html', projects=myprojects)
    
    @app.route("/project/")
    @app.route("/project/<pid>")
    def show_project(pid=None):
        if pid is None:
            flash("A valid project id is required for this page")
            return redirect(url_for('index'))

        from rc_bookmark_catcher.models import Project
        myproject = Project.query.get(pid)
        if myproject is None:
            flash(f'Could not find pid = {pid}')
            return redirect(url_for('index'))

        return render_template('project.html', project = myproject)

    @app.route("/project/new", methods = ['POST'])
    def new_project():
        from rc_bookmark_catcher.models import Project
        from rc_bookmark_catcher.redcap import make_project_from_token
        from rc_bookmark_catcher.redcap import fetch_project_instruments
        from rc_bookmark_catcher.redcap import fetch_project_fields
        flash('Placeholder for the new page')
        myapitoken = request.form.get('api_token', None)
        if myapitoken is None:
            flash('No API Token was in posted form')
            return redirect(url_for('index'))
        
        mycount = Project.query.filter(Project.api_token==myapitoken).count()
        if mycount > 0: 
            flash(f'Cannot proceed; {mycount} projects already exist with this API Token')
            return redirect(url_for('index'))

        try: 
            myproject = make_project_from_token( myapitoken ) 
            db.session.add( myproject ) 
        except RuntimeError as e:
            flash(f'There was an error while using the API token to create a project: {e}')
            return redirect(url_for('index'))

        try:
            myinstruments = fetch_project_instruments( myproject )
            db.session.add_all( myinstruments )
        except RuntimeError as e:
            flash(f'There was an error while building instruments for the project: {e}')
            return redirect(url_for('index'))

        try:
            myvariables = fetch_project_fields( myproject )
            db.session.add_all( myvariables )
        except RuntimeError as e:
            flash(f'There was an error while importing variables for the project: {e}')
            return redirect(url_for('index'))
        
        db.session.commit()
        flash(f'Created Project [pid = {myproject.project_id}] - {myproject.project_title}')
        return redirect(url_for('show_project', pid=myproject.project_id))

    ##################
    # Shell commands #
    ##################
    
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


    ###########

    return app
