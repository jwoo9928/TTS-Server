from app import create_app
app = create_app()
# gunicorn -w 1 --worker-class gthread --threads 1 -b 0.0.0.0:8080 wsgi:app
'''
모델과 함수 호출이 스레드에 안전하도록 관리됩니다.
각 요청마다 고유한 모델 인스턴스를 사용하지 않고, 싱글턴 패턴을 이용하여 모든 스레드에서 하나의 모델 인스턴스를 공유하도록 구성했습니다.
이는 메모리 사용을 최적화하면서도 동시성 문제를 방지합니다.
'''