FROM python:3.13.0-alpine3.20

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./src /app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]