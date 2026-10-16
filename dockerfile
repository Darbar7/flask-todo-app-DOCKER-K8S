FROM python:3.10-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /app/wheels /images/wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/images/wheels -r requirements.txt
COPY templates/ ./templates/
COPY App.py .
EXPOSE 5000
CMD ["python", "App.py"]
