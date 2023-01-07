FROM python:alpine
RUN mkdir /app
ADD . /app
WORKDIR /app
CMD ["python", "main.py"]

