# 기본 이미지를 python3.8.1 로 설정
FROM python:3.8.1

# tesseract-ocr 업데이트 또는 설치하기
#RUN apt-get update && apt-get install -y tesseract-ocr
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev pkg-config tesseract-ocr-kor

# docker 한글 패치를 위한 설정
RUN apt-get update && apt-get install -y locales
RUN locale-gen ko_KR.UTF-8
ENV LC_ALL ko_KR.UTF-8

# docker 내에서 /ImageProcessing 라는 이름의 폴더 생성
RUN mkdir /ImageProcessing
# docker 내에서 코드를 실행할 폴더 위치를 /ImageProcessing 로 지정
WORKDIR /ImageProcessing
# 로컬의 requirements.txt 파일을 docker /ImageProcessing/ 폴더로 마운트
ADD requirements.txt /ImageProcessing
# docker 내 requirements.txt 파일을 이용하여 패키지 설치
RUN pip install -r requirements.txt
# 로컬 내 현재 위치에 있는 모든 파일 및 폴더를 docker 의 /ImageProcessing/ 폴더로 마운트
ADD . /ImageProcessing