FROM python:3

ADD src /

RUN pip install --upgrade -r requirements.txt

CMD ["python", "app.py"]
