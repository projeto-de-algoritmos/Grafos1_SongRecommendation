FROM python:3.8

COPY requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip install -r requirements.txt
COPY . /code
CMD [sh, -c, "pip install -r requirements.txt && python web/app.py"]