FROM python:3.8.1
RUN mkdir /ImageProcessing
WORKDIR /ImageProcessing

ADD requirements.txt /ImageProcessing/
RUN pip install -r requirements.txt
ADD . /ImageProcessing/