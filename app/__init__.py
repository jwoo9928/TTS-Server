from flask import Flask
from .routes import configure_routes
from .xtts_api import initialize_model

def create_app():
    app = Flask(__name__)
    configure_routes(app)
    initialize_model(app)  # 여기서 생성된 app 인스턴스 전달
    return app
