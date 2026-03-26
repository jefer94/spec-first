FROM python:3.14-rc-slim

WORKDIR /github/workspace

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY src/ /app/src/

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "-m", "src.main"]
