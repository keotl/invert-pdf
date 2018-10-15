FROM amd64/ubuntu:bionic

WORKDIR /app

COPY pdfinvert /app/pdfinvert
COPY requirements.txt /app
COPY application.yml /app
RUN apt update && apt install -y python3-pip ghostscript texlive-extra-utils

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

RUN apt update && apt install -y imagemagick


COPY policy.xml /etc/ImageMagick-6/policy.xml
ENV PYTHONPATH /app

CMD ["/bin/bash", "-c", "gunicorn --bind=0.0.0.0:$PORT --workers=2 --threads=4 --timeout 1800 --graceful-timeout 400 pdfinvert.main"]
