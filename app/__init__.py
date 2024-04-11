from flask import Flask
from .routes import configure_routes

def create_app():
    app = Flask(__name__)
    configure_routes(app)
    return app
# gunicorn -w 2 --worker-class gthread --threads 2 -b 0.0.0.0:8020 a_server:app