FROM centos/python-36-centos7
COPY . /app
WORKDIR /app
ENV ENV="production"
USER root

RUN env
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#CMD env
#CMD alembic init mes_alembic
#CMD alembic stamp head
#CMD alembic revision --autogenerate -m "heroku"
#CMD alembic upgrade head

CMD gunicorn  -k gunicorn.workers.ggevent.GeventWorker -w 1 -b 0.0.0.0:$PORT __init__:app
