FROM python:2.7.14         
ADD . /todo
WORKDIR /todo
EXPOSE 5000
RUN pip install --process-dependency-links -r requirements.txt
ENTRYPOINT ["python", "server.py"]