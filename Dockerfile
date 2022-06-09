FROM tiangolo/meinheld-gunicorn:python3.9

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt;

COPY . /app
