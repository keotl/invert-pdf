FROM amd64/ubuntu:latest

WORKDIR /app

COPY pdfinvert /app/pdfinvert
COPY requirements.txt /app
COPY application.yml /app
RUN apt update && apt install -y python3-pip

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8080

RUN apt update && apt install -y imagemagick

RUN rm /etc/ImageMagick-6/policy.xml

ENV PYTHONPATH /app

CMD ["python3", "/app/pdfinvert/main.py"]