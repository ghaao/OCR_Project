import logging

import requests

logger = logging.getLogger('django_info')

def requestForBW(clofferId, docTypCd, reqtDttm, errCode, outText):
    headers = {'Content-Type': 'application/json; charset=utf-8',
                'Cache-Control': 'no-cache'}
    # cookies = {'session_id': 'sorryidontcare'}
    url = 'https://naver.com'
    data = {
        'CLOFFER_ID': clofferId,
        'DOC_TYP_CD': docTypCd,
        'REQT_DTTM': reqtDttm,
        'ERR_CD': errCode,
        'RESULT': outText
    }

    response = requests.post(url=url, headers=headers, data=data)
    logger.info('Success send RESTful API to BW - ' + str(data))

    if(response.ok):
        logger.info('Success BW was received REST api request.')
    else:
        logger.info('Error to send REST api request. Response Code(' + str(response.status_code) +')')