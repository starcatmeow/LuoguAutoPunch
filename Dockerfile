FROM python:3.8-buster

WORKDIR /app

RUN wget -q https://dl-ssl.google.com/linux/linux_signing_key.pub && apt-key add linux_signing_key.pub && rm linux_signing_key.pub
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
ENV DISPLAY=:99
ENV TF_CPP_MIN_LOG_LEVEL=2
COPY requirements.txt /app
RUN pip install --upgrade pip && pip install -r requirements.txt && rm requirements.txt
COPY app.py /app

ENTRYPOINT [ "python", "app.py" ]
