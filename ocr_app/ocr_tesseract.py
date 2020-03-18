import configparser
import logging
import os

from PIL import Image  # pip install pillow
from django.utils import timezone
from pytesseract import *  # pip install pytesseract

from ocr_app import requestREST
from ocr_app.models import SPOILER_LOG

logger = logging.getLogger('django_info')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#Config Parser 초기화
config = configparser.ConfigParser()
#Config File 읽기
config.read(os.path.dirname(os.path.realpath(__file__)) + os.sep + 'properties' + os.sep + 'property.ini')

#이미지 -> 문자열 추출
def ocrToStr(fullPath, outTxtPath, fileName, clofferId, docTypCd, reqtDttm, lang='eng'): #디폴트는 영어로 추출
    #이미지 경로
    img = Image.open(fullPath)
    txtName = os.path.join(outTxtPath,fileName.split('.')[0])

    #추출(이미지파일, 추출언어, 옵션)
    #preserve_interword_spaces : 단어 간격 옵션을 조절하면서 추출 정확도를 확인한다.
    #psm(페이지 세그먼트 모드 : 이미지 영역안에서 텍스트 추출 범위 모드)
    #psm 모드 : https://github.com/tesseract-ocr/tesseract/wiki/Command-Line-Usage
    outText = image_to_string(img, lang=lang, config='--psm 1 -c preserve_interword_spaces=1')

    logger.info('Extract FileName ->>> : ' + str(fullPath))

    # 추출 문자 텍스트 파일 쓰기
    strToTxt(txtName, outText)

    # Result Model SQLite저장
    SPOILER_LOG.objects.filter(CLOFFER_ID=clofferId, DOC_TYP_CD=docTypCd, REQT_DTTM=reqtDttm).update(PRC_DTTM=timezone.now(), PRC_FLG='Y', MSG_CTNT=outText)

    # OCR 처리 된 파일 삭제 (이미지이므로 파일을 삭제하여 용량을 확보)
    os.remove(fullPath)

    # Fail Requset(REST) 전송
    requestREST.requestForBW(clofferId, docTypCd, '00')

    # Result Log 저장
    logger.info(str(clofferId) + ' - OCR_RESULT._LOG instance is stored to sqllite.')


#문자열 -> 텍스트파일 개별 저
def strToTxt(txtName, outText):
    with open(txtName + '.txt', 'w', encoding='utf-8') as f:
        f.write(outText)

#메인 시작
def startSpoilerProcess(clofferId, docTypCd, reqtDttm):
    errCode='00'
    prcCnt=0

    try:
        #텍스트 파일 저장 경로
        outTxtPath = os.path.dirname(os.path.realpath(__file__))+ config['Path']['OcrTxtPath']

        #OCR 추출 작업 메인
        for root, dirs, files in os.walk(os.path.dirname(os.path.realpath(__file__)) + config['Path']['OriImgPath']):
            for fname in files:

                if str(clofferId)+docTypCd+reqtDttm in fname:
                    fullName = os.path.join(root, fname)

                    #한글+영어 추출(kor, eng , kor+eng)
                    ocrToStr(fullName, outTxtPath, fname, clofferId, docTypCd, reqtDttm, 'kor+eng')
                    prcCnt+=1


        # 처리 갯수가 0이면
        if prcCnt == 0:
            errCode = '19'
            logger.info(str(clofferId) + ' - 처리된 파일이 0개인 오류')

    except ChildProcessError:
        errCode = '11'
        logger.info(str(clofferId) + ' - 하위 프로세스(프로그램이 실행한 외부 프로그램)에서 오류 발생')
    except FileExistsError:
        errCode = '12'
        logger.info(str(clofferId) + ' - 이미존재하는 파일/디렉터리를 새로 생성하려 할 때 오류')
    except FileNotFoundError:
        errCode = '13'
        logger.info(str(clofferId) + ' - 존재하지 않는 파일/디렉터리에 접근하려 할 때 오류')
    except IsADirectoryError:
        errCode = '14'
        logger.info(str(clofferId) + ' - 파일을 위한 명령을 디렉터리에 실행할 때 오류')
    except NotADirectoryError:
        errCode = '15'
        logger.info(str(clofferId) + ' - 디렉터리를 위한 명령을 실행할 때 오류')
    except PermissionError:
        errCode = '16'
        logger.info(str(clofferId) + ' - 명령을 실행할 권한이 없을 때 오류')
    except TimeoutError:
        errCode = '17'
        logger.info(str(clofferId) + ' - 명령의 수행 시간이 기준을 초과했을 때 오류')
    except EOFError:
        errCode = '18'
        logger.info(str(clofferId) + ' - (파일에서) 읽어들일 데이터가 더이상 없을 때 오류')
    except:
        errCode = '99'
        logger.info(str(clofferId) + ' - 기타 오류 (관리자에게 문의)')

    finally:
        # Fail Requset(REST) 전송
        requestREST.requestForBW(clofferId, docTypCd, errCode)


def startSpoilerTest(fullPath):
    fullPath = BASE_DIR + fullPath
    img = Image.open(fullPath)
    outText = image_to_string(img, lang='kor+eng', config='--psm 1 -c preserve_interword_spaces=1')

    return outText