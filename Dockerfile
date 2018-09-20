FROM python:3.7

ENV DJANGO_CONFIGURATION Docker

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
ADD . /usr/src/app
RUN pip install -r requirements.txt

#test change  ff

CMD ["gunicorn", "-c", "gunicorn_conf.py", "--chdir", "ndd-app", "ndd.wsgi:application", "--reload"]
