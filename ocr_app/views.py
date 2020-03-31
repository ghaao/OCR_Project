import logging

from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ocr_app import ocr_tesseract, requestREST
from ocr_app.models import SPOILER_LOG, Photo
from .forms import PhotoForm
from .serializers import OCRSerializer

logger = logging.getLogger('django_info')

clofferId = 0
docTypCd = ''
reqtDttm = '00000000000000'

class BasicUploadView(View):
    def get(self, request):
        photos_list = Photo.objects.all()
        return render(self.request, 'photos/basic_upload/index.html', {'photos': photos_list})

    def post(self, request):
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save()

            # 문서유형코드 확인
            if len(photo.file.name) < 17:
                data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url, 'imagetext': '잘못된 파일명입니다. (ex-123456780120200323000000)'}
            else:
                #문서유형코드 알아내기
                docTypCd = photo.file.name[15:17]
                imagetext = ocr_tesseract.startSpoilerTest(photo.file.url, docTypCd)
                data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url, 'imagetext': imagetext}

        else:
            data = {'is_valid': False}
        return JsonResponse(data)


class ProgressBarUploadView(View):
    def get(self, request):
        photos_list = Photo.objects.all()

        return render(self.request, 'photos/progress_bar_upload/index.html', {'photos': photos_list})

    def post(self, request):
        form = PhotoForm(self.request.POST, self.request.FILES)

        if form.is_valid():
            photo = form.save()

            # 문서유형코드 확인
            if len(photo.file.name) < 17:
                data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url, 'imagetext': '잘못된 파일명입니다. (ex-123456780120200323000000)'}
            else:
                #문서유형코드 알아내기
                docTypCd = photo.file.name[15:17]
                imagetext = ocr_tesseract.startSpoilerTest(photo.file.url, docTypCd)
                data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url, 'imagetext': imagetext}

        else:
            data = {'is_valid': False}

        return JsonResponse(data)


class DragAndDropUploadView(View):
    def get(self, request):
        photos_list = Photo.objects.all()
        return render(self.request, 'photos/drag_and_drop_upload/index.html', {'photos': photos_list})

    def post(self, request):
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            photo = form.save()

            # 문서유형코드 확인
            if len(photo.file.name) < 17:
                data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url, 'imagetext': '잘못된 파일명입니다. (ex-123456780120200323000000)'}
            else:
                #문서유형코드 알아내기
                docTypCd = photo.file.name[15:17]
                imagetext = ocr_tesseract.startSpoilerTest(photo.file.url, docTypCd)
                data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url, 'imagetext': imagetext}

        else:
            data = {'is_valid': False}
        return JsonResponse(data)


def clear_database(request):
    for photo in Photo.objects.all():
        photo.file.delete()
        photo.delete()
    return redirect(request.POST.get('next'))



@api_view(['GET', 'POST'])
def spoiler_extract(request):
    # POST로만 Requset를 받는다.
    if request.method == 'GET':
        serializer = OCRSerializer(data=request.data)
        logger.info("HttpResponse(Get) - BAD REQUEST(400) " + str(request.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
        # Global 변수 설정 - Spoiler 작업 변경 처리를 위한 PK를 넘긴다.
        global clofferId, docTypCd, reqtDttm

        clofferId = int(request.data['CLOFFER_ID'])
        docTypCd = str(request.data['DOC_TYP_CD'])
        reqtDttm = str(request.data['REQT_DTTM'])

        logger.info("HttpResponse RECEIVE > CLOFFER_ID-[" + str(clofferId) + "] / DOC_TYP_CD-["+docTypCd+"] / PRC_DTTM-["+reqtDttm+"]")

        # 에러코드 확인 - request를 받을 시 Validation을 통해 정상일 경우만 Spoiler 실행. 정상이 아닐 경우, 바로 Response 보냄
        errCode = '00'
        outText = ''

        # 예외처리
        if clofferId is None or clofferId == 0:
            logger.info("WRONG DATA > CLOFFER_ID가 null인 오류")
            errCode = '01'
            outText = 'CLOFFER_ID가 null인 오류'
        elif docTypCd is None or docTypCd == '':
            logger.info("WRONG DATA > DOC_TYP_CD이 null 오류")
            errCode = '02'
            outText = 'DOC_TYP_CD가 null인 오류'
        elif reqtDttm is None or reqtDttm == '' or len(reqtDttm) != 14:
            logger.info("WRONG DATA > PRC_DTTM이 null 또는 데이터타입이 맞지 않는 오류.")
            errCode = '03'
            outText = 'PRC_DTTM이 null 또는 데이터타입이 맞지 않는 오류.'

        # 변수가 정확하다면 Spoiler 진행.
        if errCode == '00':
            # OCR 진행을 위한 Serializer 생성
            serializer = OCRSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                #response = afterResponse(serializer.data)
                #return response
                errCode, outText = ocr_tesseract.startSpoilerProcess(clofferId, docTypCd, reqtDttm)
                logger.info("HttpResponse RESPONSE > 결과[" + errCode +"] - " + str(outText))
                return Response({'CLOFFER_ID': clofferId,
                                'DOC_TYP_CD': docTypCd,
                                'REQT_DTTM': reqtDttm,
                                'ERR_CD': errCode,
                                'RESULT': outText})
            else:
                logger.info("HttpResponse RESPONSE > BAD REQUEST(400) " + str(request.data))
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.info("HttpResponse RESPONSE > 정확하지 않은 변수로 오류 처리 CLOFFER_ID-[" + str(clofferId) + "] / DOC_TYP_CD-[" + docTypCd + "] / PRC_DTTM-[" + reqtDttm + "]")
            #requestREST.requestForBW(clofferId, docTypCd, reqtDttm, errCode, outText)
            return Response({'CLOFFER_ID': clofferId,
                             'DOC_TYP_CD': docTypCd,
                             'REQT_DTTM': reqtDttm,
                             'ERR_CD': errCode,
                             'RESULT': outText})

class afterResponse(HttpResponse):
    def close(self):
        super(afterResponse, self).close()

        if self.status_code == 200:
            logger.info('HttpResponse - successful(%s)' % self.status_code)

            # OCR 진행
            logger.info('Spoiler Start - ' + str(clofferId))
            ocr_tesseract.startSpoilerProcess(clofferId, docTypCd, reqtDttm)
            logger.info('Spoiler Exit - ' + str(clofferId))


@api_view(['GET', 'PUT', 'DELETE'])
def spoiler_extract_list(request, pk):
    try:
        snippet = SPOILER_LOG.objects.get(pk=pk)
    except SPOILER_LOG.DoesNotExist:
        logger.info("NOT FOUND(404) - " + str(request.data))
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OCRSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = OCRSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            logger.info("BAD REQUEST(400) - " + str(request.data))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

""" 
#    @detail_route 부분을 데코레이터라고 부릅니다.
#    이 부부은 ViewSet에서 기본적으로 제공하는 Action이외의 메서드를 라우팅할 때 사용합니다.
     @detail_route(methods=['post'])9
     def set_password(self, request, pk=None):
        return Response({'status': 'password set'})
       
    데코레이터에는 두 가지 종류가 있습니다.
    detail_route → 특정 아이템을 반환하는 메서드일 때 사용합니다.
    list_route → 아이템 목록을 반환할 때 사용합니다.
"""