FROM tiangolo/meinheld-gunicorn:python3.10

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt;

COPY . /app
