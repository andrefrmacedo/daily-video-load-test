FROM --platform=linux/amd64 python:3.13-alpine

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.20/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.20/community" >> /etc/apk/repositories

# install chromedriver
RUN apk update
RUN apk add chromium chromium-chromedriver bash libc6-compat


COPY . /srv/daily-video-load/

WORKDIR /srv/daily-video-load/

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "load_test.py"]
