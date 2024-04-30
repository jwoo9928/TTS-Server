from app import create_app
app = create_app()
# gunicorn -w 1 --worker-class gthread --threads 1 -b 0.0.0.0:8080 wsgi:app
