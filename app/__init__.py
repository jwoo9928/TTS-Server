from flask import Flask
from .routes import configure_routes
from .xtts_api import AppContext

def create_app():
    app = Flask(__name__)
    app_context = AppContext.get_instance()  # 싱글턴 인스턴스를 사용하여 애플리케이션 컨텍스트를 가져옵니다.
    configure_routes(app, app_context)
    app_context.initialize_model()  # 모델 초기화
    return app