FROM python:3.6.3
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000

CMD gunicorn  -k gunicorn.workers.ggevent.GeventWorker -w 4 -b 0.0.0.0:8000 main:app
