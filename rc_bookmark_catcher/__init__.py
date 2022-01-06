import os
import click
from flask import Flask, render_template, request, flash, current_app, abort
from flask import url_for, redirect

from flask_bootstrap import Bootstrap

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension()


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
    toolbar.init_app(app)


    ##########
    # ROUTES #
    ##########

    # HOME

    # TODO: REFACTOR
    @app.route("/")
    def index():
        from rc_bookmark_catcher.models import Project, Template
        myprojects = Project.query.order_by(Project.pid).all()
        mytemplates = Template.query.order_by(Template.template_name).all()
        return render_template('home.html', projects = myprojects, templates = mytemplates )

    # PROJECTS
    
    # TODO: REFACTOR
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

    # TODO: REFACTORED NEW PROJECT PAGES NEED TO PUT FIELDS AND INSTRUMENTS BACK IN
    @app.route("/project/new")
    def new_project():
        return render_template('newproject.html')

    @app.route('/project/add_confirm', methods = ['post'])
    def add_confirm_project():
        mystu = request.form.get('stu', None)
        mytoken = request.form.get('api_token', None)

        if not mystu or not mytoken:
            flash('Need both an STU # and an API TOKEN','error')
            return redirect(request.referrer)

        from rc_bookmark_catcher import redcap,models

        # Check if the API token was already used. To enforce that project can only be associated with 1 STU#
        mycount = models.Project.query.filter(models.Project.api_token==mytoken).count()
        if mycount > 0: 
            flash(f'Cannot proceed; {mycount} projects already exist with this API Token', 'error')
            return redirect(request.referrer)
        
        # Create a project object via REDCap call and populate with fetched attributes AND the STU#
        try:
            myproject = redcap.make_project_from_token( mytoken, mystu )
        except RuntimeError as e:
            flash(f'There was an error while using the API token to create a project: {e}', 'error')
            return redirect(request.referrer)

        flash('Retrieved a project from REDCap')
        return render_template('addconfirmproject.html', project = myproject)

    @app.route("/project/add", methods = ['post'])
    def add_project():
        from rc_bookmark_catcher import models
        myproject = models.Project(
            pid = request.form.get('pid', None),
            stu = request.form.get('stu', None),
            project_title = request.form.get('project_title', None),
            api_token = request.form.get('api_token', None),
            is_longitudinal = request.form.get('is_longitudinal', None),
            has_repeating_instruments_or_events = request.form.get('has_repeating_instruments_or_events', None),
            surveys_enabled = request.form.get('surveys_enabled', None)
        )

        try: 
            db.session.add(myproject) 
            db.session.commit()
        except RuntimeError as e:
            flash(f'Could not commit project {myproject.pid} into database','error')
            return redirect(url_for('index'))

        flash(f'Added project (pid={myproject.pid}, stu={myproject.stu}) to DB')
        return redirect(url_for('show_project', pid=myproject.pid))


    # TEMPLATES

    # TODO: REFACTOR
    @app.route('/template/')
    @app.route('/template/<template_name>')
    def show_template(template_name = None):
        if template_name is None:
            flash(f'A valid template name is required for this page')
            return redirect(url_for('index'))

        from rc_bookmark_catcher.models import Template
        mytemplate = Template.query.get(template_name)
        if mytemplate is None:
            flash(f'Could not find Template with template_name = {template_name}')
            return redirect(url_for('index'))
        
        return render_template('template.html', template = mytemplate)

    #########################
    # REDCap Landing Routes #
    #########################

    @app.route('/redcap/push/s', methods = ['get'])
    def redcap_simple():
        # We will probably not use this. Kept here as demo of what simple link does.
        return render_template('simplebookmark.html')

    @app.route('/redcap/push/a', methods = ['post'])
    def redcap_advanced():
        from rc_bookmark_catcher import redcap,models
        myauthkey = request.form.get('authkey', None)

        # Send a 401 Unauthorized if the token is a dud 
        if myauthkey is None:
            abort(401)
        try:
            my_advanced_link_info = redcap.fetch_advanced_link_info(myauthkey)
        except RuntimeError as e:
            abort(401)

        # RECORD and EVENT are appended to the URL not part of the authkey-mediated info
        my_advanced_link_info['get_record'] = request.args.get('record', None)
        my_advanced_link_info['get_event'] = request.args.get('event', None)

        # Check if the project referenced is registered in the system and associated with a study
        # If not registered then Send a 401 Unauthorized error or recover gracefully in CTMS
        myproject = db.session.execute( db.select(models.Project).where(models.Project.pid == my_advanced_link_info['project_id']) ).scalar()
        if myproject is None:
            abort(401)

        # Should probably kick them out if the username (i.e. netid) is not allowed in the study
        # def check_apl_or_something_in_CTMS( myresponse['username'], myproject.stu ) --> True|False
        # (Not done here)

        if my_advanced_link_info['get_record'] is None:
            flash('The link was not clicked from within a record. No further actions can be taken to fetch records', 'warning')
            return render_template('advland_instrument_norecord.html', redcap_response = my_advanced_link_info, redcap_project = myproject )
        else:
            #myrecords = redcap.fetch_advanced_link_records(myproject, my_advanced_link_info)
            myperson = redcap.fetch_advanced_link_person(myproject, my_advanced_link_info)
            myselect2_instrument_array = redcap.fetch_project_instruments_as_select2(myproject)

        return render_template('advland_instrument_select.html', 
            redcap_response = my_advanced_link_info, 
            redcap_project = myproject, 
            person = myperson,
            select2_instrument_array = myselect2_instrument_array
            )

    @app.route('/redcap/instrumentconfirm', methods=['post'])
    def show_instrument():
        flash('There was an error loading HOV mappings for this instrument', 'error')
        return render_template('base.html')


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
