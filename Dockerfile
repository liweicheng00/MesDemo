FROM python:3.6.3
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD gunicorn  -k gunicorn.workers.ggevent.GeventWorker -w 4 -b 0.0.0.0:8000 __init__:app
