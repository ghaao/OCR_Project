#-*-coding:utf8;-*-
'''
OCR for indemnity insurance receipt
Kim Namkil (2019.11.26)
Add RBM mode, Diagnosis mode
'''
import os

from ocr_app.spoiler.document_analyzer import DocumentAnalyzer
from ocr_app.spoiler.mapper import WordMapper
from ocr_app.static.properties.enumeration import DTC

FILENAME = "/home/nkkim/ocrProject/sample/photo/rbm/modified_rbm_photo.jpg"
USERWORD_FILE = os.path.dirname(os.path.realpath(__file__)) + "/static/words/RBM_RECP_WORD_LIST.txt"

IMAGE_TYPE = 2 #scan
DPI = 200

# DPI, x, y, m, font_size = 200, 1, 1, 1, 15
DPI, x, y, m, font_size = 200, 0.25, 0.25, 4, 25 #-> 진단서 셋팅 테이블 인식 시에 사이즈 조정필요

# DPI = 400

if DPI == 400 : 
    x, y, m, font_size = 0.5, 0.5, 2, 35

# 글자 및 테이블 인식 모듈
document_analyzer = DocumentAnalyzer()
# 이미지 파일 셋팅 P-> photo S->scan
document_analyzer.set_image_file(FILENAME, image_type=IMAGE_TYPE)

document_analyzer.show_image()

# 테이블 구조 인식
table_coords = document_analyzer.detect_table(x=x, y=y, multi=m)
# 글자 인식
document_analyzer.detect_character()
# 신규 이미지 오브젝트를 만들고 인식한 테이블을 그린다.
document_analyzer.visualize_table()
# 신규 이미지 오브젝트에 인식한 글자를 그린다.
document_analyzer.visualize_character(font_size= font_size) 
# 신규 이미지 오브젝트 시각화
document_analyzer.show_recognized()

# 인식한 글자의 좌표와 인식한 테이블의 좌표를 맵핑하여 글자 뭉치 생성
table_contents = document_analyzer.combine_coordinates()

# 실손 영수증 단어 파일 (실손 영수증에 있는 필요 단어 설정 파일 읽기)
menu_words = []
with open(USERWORD_FILE, 'r') as f:   
    for line in f.readlines():
        line = line[:-1]
        menu_words.append(line.split(','))
# 테이블 구조의 데이터를 실손 영수증 단어와 비교하여 의료비별 금액을 유추한다.
word_mapper = WordMapper(menu_words, table_contents, table_coords, dtc = DTC.MEDICAL_RECEIPT)
word_mapper.word_mapping()
# 결과 프린트
word_mapper.get_mapping_results()
# 결과 엑셀로 내보내기
# word_mapper.get_mapping_results_excel()
