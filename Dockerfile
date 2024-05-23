FROM python:3.8.5-slim-buster

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements /app
RUN pip install -r requirements

COPY jobscryer.py /app
COPY email_alert.py /app
COPY jobscryer_schedule.py /app
COPY postgres.py /app

CMD ["python", "jobscryer_schedule.py"]