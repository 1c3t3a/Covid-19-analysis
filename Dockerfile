FROM python:3.7.7
COPY . /data
RUN pip3 install -r /data/requirements.txt
EXPOSE 5000
CMD python3 /data/src/rest/app.py
