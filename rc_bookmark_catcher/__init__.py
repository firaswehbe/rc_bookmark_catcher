from flask import Flask, render_template
from flask_bootstrap import Bootstrap

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    @app.route("/")
    def index():
        return render_template('base.html')
    
    Bootstrap(app)

    return app

