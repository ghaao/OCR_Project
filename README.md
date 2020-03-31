# OCR_Project(Spoiler)
spoiler
spoiler is designed to recognize hospital documents for insurance submission based on tesseract.

# Requirements
Requires libtesseract (>=4.00) and libleptonica

On Ubuntu 18.04:

$ apt-get install tesseract-ocr libtesseract-dev libleptonica-dev pkg-config
and check the requirements.txt

$ pip install -r requirements.txt
Download kor.traineddata and kor_vert.traineddata from https://github.com/tesseract-ocr/tessdata_best and move them to /usr/share/tesseract-ocr/4.00/tessdata
