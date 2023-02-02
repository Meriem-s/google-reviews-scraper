FROM python:3.9-alpine
RUN pip install --upgrade pip

WORKDIR /app
COPY . /app

ENV SCRAPY_SETTINGS_MODULE google_reviews.settings

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

CMD ["python3", "cli.py", "Rabauke Bar", "-o", "reviews.csv"]