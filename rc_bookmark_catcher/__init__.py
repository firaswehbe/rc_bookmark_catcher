from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return f"Testing {__name__} \n\
        Instant  = {app.instance_path}"

    return app

