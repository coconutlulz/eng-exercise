FROM python:3

COPY . /app
WORKDIR /app

RUN pip install --upgrade -r requirements.txt

WORKDIR /app/src
CMD ["python", "app.py"]
