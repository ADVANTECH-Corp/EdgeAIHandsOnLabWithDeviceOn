FROM python:3.7.16-slim

WORKDIR /ws 

ADD . /ws

RUN pip3 install -r requirements.txt

CMD ["sh", "setup_opencv.sh"]
