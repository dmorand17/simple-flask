# Should update this to use python:3 instead
FROM python:3.10-slim-buster

WORKDIR /app
# We copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt .

RUN pip install -r requirements.txt
COPY app.py .

EXPOSE 5000
ENV FLASK_APP=app.py
ENTRYPOINT ["flask", "run", "--host", "0.0.0.0"]
