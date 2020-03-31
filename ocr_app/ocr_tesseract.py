import logging
import os

from django.utils import timezone

from ocr_app.models import DOC_TYP_WORD_LIST
# from ocr_app import requestREST
from ocr_app.models import SPOILER_LOG
from ocr_app.spoiler.spoiler import Spoiler
from ocr_app.static.properties.enumeration import RM, DTC, ITC

logger = logging.getLogger('django_info')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# REST 요청으로 들어온 경우
def startSpoilerProcess(clofferId, docTypCd, reqtDttm):
    errCode='99'
    prcCnt=0
    outText='Fail'

    try:
        # OCR 추출 작업 메인
        for root, dirs, files in os.walk(os.path.dirname(__file__)  + os.sep + 'resource' + os.sep + 'orc_ori_image'):
            for fname in files:

                # 파일 존재 시, Spoiler 실행
                if str(clofferId)+docTypCd+reqtDttm in fname:
                    # File root 설정.
                    fileFullName = os.path.join(root, fname)
                    # 문서유형코드별 추출 Word 조회
                    DOC_TYPS = DOC_TYP_WORD_LIST.objects.filter(DOC_TYP_CD=docTypCd, USE_FLG='Y')

                    # DB에 존재하는 문서유형코드 추출 Word 없을 시 Error
                    if DOC_TYPS is None or len(DOC_TYPS) == 0:
                        errCode = '04'
                        outText = '지원하지 않는 문서 유형입니다. 문서유형코드를 다시 한 번 확인해주세요.'

                    else:
                        documentTypCode = getDocumentTypeCode(docTypCd)

                        # 추출 Word List 작성
                        item_list = []
                        for data in DOC_TYPS:
                            line = []

                            if data.ITM_STR_VLU01 is not None:
                                line.append(data.ITM_STR_VLU01)
                            if data.ITM_STR_VLU02 is not None:
                                line.append(data.ITM_STR_VLU02)
                            if data.ITM_STR_VLU03 is not None:
                                line.append(data.ITM_STR_VLU03)
                            if data.ITM_STR_VLU04 is not None:
                                line.append(data.ITM_STR_VLU04)
                            if data.ITM_STR_VLU05 is not None:
                                line.append(data.ITM_STR_VLU05)
                            if data.ITM_STR_VLU06 is not None:
                                line.append(data.ITM_STR_VLU06)
                            if data.ITM_STR_VLU07 is not None:
                                line.append(data.ITM_STR_VLU07)
                            if data.ITM_STR_VLU08 is not None:
                                line.append(data.ITM_STR_VLU08)
                            if data.ITM_STR_VLU09 is not None:
                                line.append(data.ITM_STR_VLU09)
                            if data.ITM_STR_VLU10 is not None:
                                line.append(data.ITM_STR_VLU10)

                            item_list.append(line)

                        # Spoiler 실행
                        test_ocr = Spoiler(run_mode=RM.PROD)
                        outText = test_ocr.publish(document_type_code=DTC.MEDICAL_CERTIFICATE, image_type_code=ITC.SCAN,
                                     file_path=fileFullName, item_list=item_list)

                        # 정상처리 설정
                        errCode = '00'

                    # 결과 전송한 파일 삭제.
                    os.remove(fileFullName)

                    # 처리 수 확인을 위한 Flag
                    prcCnt+=1

        # 처리 갯수가 0이면
        if prcCnt == 0:
            errCode='19'
            outText='처리된 파일이 0개인 오류'

    except ChildProcessError:
        errCode='11'
        outText='하위 프로세스(프로그램이 실행한 외부 프로그램)에서 오류 발생'
    except FileExistsError:
        errCode='12'
        outText='이미존재하는 파일/디렉터리를 새로 생성하려 할 때 오류'
    except FileNotFoundError:
        errCode='13'
        outText='존재하지 않는 파일/디렉터리에 접근하려 할 때 오류'
    except IsADirectoryError:
        errCode='14'
        outText='파일을 위한 명령을 디렉터리에 실행할 때 오류'
    except NotADirectoryError:
        errCode='15'
        outText='디렉터리를 위한 명령을 실행할 때 오류'
    except PermissionError:
        errCode='16'
        outText='명령을 실행할 권한이 없을 때 오류'
    except TimeoutError:
        errCode='17'
        outText='명령의 수행 시간이 기준을 초과했을 때 오류'
    except EOFError:
        errCode='18'
        outText='(파일에서) 읽어들일 데이터가 더이상 없을 때 오류'
    except Exception as e:
        errCode='99'
        outText=str(e)[0:1000]

    finally:
        logger.info("Final result ["+str(clofferId) + "] - "+ str(outText)+"(Error-Code = "+errCode+")")

        # 처리 로그 DB 저장
        SPOILER_LOG.objects.filter(CLOFFER_ID=clofferId, DOC_TYP_CD=docTypCd, REQT_DTTM=reqtDttm).update(
            PRC_DTTM=timezone.now(), PRC_TYP_CD=errCode, PRC_FLG='Y', MSG_CTNT=outText)

        # Result Requset(REST API) 전송
        #requestREST.requestForBW(clofferId, docTypCd, reqtDttm, errCode, outText)

        # Response 결과 값 return
        return errCode, outText

# http://127.0.0.1/spoiler_app/progress-bar-upload/ 주소로 들어 올 경우.
def startSpoilerTest(fullPath, docTypCd):
    # 문서유형코드별 추출 Word 조회
    DOC_TYPS = DOC_TYP_WORD_LIST.objects.filter(DOC_TYP_CD=docTypCd, USE_FLG='Y')

    # DB에 존재하는 문서유형코드 추출 Word 없을 시 Error
    if DOC_TYPS is None or len(DOC_TYPS) == 0:
        return '지원하지 않는 문서 유형입니다. 파일명 9-10번 자리의 문서유형코드를 확인해주세요.'
    else:
        fileFullName = BASE_DIR + fullPath
        documentTypCode = getDocumentTypeCode(docTypCd)

        # 추출 Word List 작성
        item_list = []
        for data in DOC_TYPS:
            line = []

            if data.ITM_STR_VLU01 is not None:
                line.append(data.ITM_STR_VLU01)
            if data.ITM_STR_VLU02 is not None:
                line.append(data.ITM_STR_VLU02)
            if data.ITM_STR_VLU03 is not None:
                line.append(data.ITM_STR_VLU03)
            if data.ITM_STR_VLU04 is not None:
                line.append(data.ITM_STR_VLU04)
            if data.ITM_STR_VLU05 is not None:
                line.append(data.ITM_STR_VLU05)
            if data.ITM_STR_VLU06 is not None:
                line.append(data.ITM_STR_VLU06)
            if data.ITM_STR_VLU07 is not None:
                line.append(data.ITM_STR_VLU07)
            if data.ITM_STR_VLU08 is not None:
                line.append(data.ITM_STR_VLU08)
            if data.ITM_STR_VLU09 is not None:
                line.append(data.ITM_STR_VLU09)
            if data.ITM_STR_VLU10 is not None:
                line.append(data.ITM_STR_VLU10)

            item_list.append(line)

    # Spoiler 실행
    test_ocr = Spoiler(run_mode=RM.WEB_TEST)
    outText = test_ocr.publish(document_type_code=documentTypCode, image_type_code=ITC.SCAN,
                               file_path=fileFullName, item_list=item_list)

    return str(outText)


def getDocumentTypeCode(docTypCd):
    documentTypCode = DTC.MEDICAL_CERTIFICATE

    if docTypCd == '01':
        documentTypCode = DTC.MEDICAL_CERTIFICATE
    elif docTypCd == '02':
        documentTypCode = DTC.MEDICAL_RECEIPT

    return documentTypCode