# Python 이미지를 기반으로 설정합니다.
FROM python:3.6

# 작업 디렉토리를 설정합니다.
WORKDIR /app

# git을 설치합니다.
RUN apt-get update && apt-get install -y git

RUN pip install gunicorn

# GitHub 저장소에서 프로젝트를 클론합니다.
RUN git clone https://github.com/jwoo9928/TTS-Server.git /app

# 의존성을 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 서버를 실행합니다. 이 명령어는 해당 프로젝트와 환경에 맞게 조정해야 할 수 있습니다.
CMD ["gunicorn", "-w", "2", "--worker-class", "gthread", "--threads", "2", "-b", "0.0.0.0:8020", "app.wsgi:app"]
