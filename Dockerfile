FROM python:3.10.0b4
COPY . /app
RUN pip3 install -r /app/requirements.txt
EXPOSE 5000
WORKDIR /app/src/rest
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]