from flask import Flask, render_template, request, flash
from flask_bootstrap import Bootstrap

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.secret_key = b'deleteme123'

    @app.route("/")
    def index():
        if request.args.get('pid') is None:
            flash("A valid project id is required for this page")
        return render_template('base.html')
    
    Bootstrap(app)

    return app

