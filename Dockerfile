FROM python:3.12-alpine
WORKDIR /app
RUN pip install flask pyyaml gunicorn
COPY app.py /app/app.py
CMD ["python", "/app/app.py"]
EXPOSE 8099
CMD ["gunicorn", "-b", "0.0.0.0:7099", "app:app"]
