module.exports = {
    apps : [{
      name: 'my-flask-app',
      script: 'gunicorn',
      args: '-w 2 --worker-class gthread --threads 2 -b 0.0.0.0:8010 wsgi:app --reload',
      interpreter: 'none',
      exec_mode: 'fork'
    }]
  };
  