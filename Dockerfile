FROM python:3.8-alpine3.10

WORKDIR /app
# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.10/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.10/community" >> /etc/apk/repositories

# install chromedriver
RUN apk update && apk add chromium chromium-chromedriver

# install requirements
RUN pip install --upgrade pip && pip uninstall numpy && pip install -r requirements.txt

ENTRYPOINT [ "python", "app.py" ]