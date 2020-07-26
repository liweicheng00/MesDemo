FROM centos/python-36-centos7
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN alembic init mes-alembic
RUN alembic revision --autogenerate -m "heroku"
RUN alembic upgrade head

CMD gunicorn  -k gunicorn.workers.ggevent.GeventWorker -w 4 -b 0.0.0.0:8000 __init__:app
