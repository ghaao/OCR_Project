from ocr_app.models import OCRInstance
from .serializers import OCRSerializer

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import ocr_tesseract
from django.http import HttpResponse

import logging
logger = logging.getLogger('django_info')

clofferId = 0

class afterResponse(HttpResponse):
    def close(self):
        super(afterResponse, self).close()

        if self.status_code == 200:
            logger.info('HttpResponse - successful(%s)' % self.status_code)

            # OCR 진행
            logger.info('OCR Start - ' + str(clofferId))
            ocr_tesseract.startOCRProcess(clofferId)
            logger.info('OCR Exit - ' + str(clofferId))

@api_view(['GET', 'POST'])
def ocr_list(request):

    if request.method == 'GET':
        snippets = OCRInstance.objects.all()
        serializer = OCRSerializer(snippets, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        global  clofferId
        clofferId = int(request.data['CLOFFER_ID'])
        logger.info("HttpResponse - RECEIVE CLOFFER_ID " + str(clofferId))

        if clofferId is None or clofferId == 0:
            logger.info("WRONG DATA - CLOFFER_ID IS NULL")
            return Response('WRONG DATA - CLOFFER_ID', status=status.HTTP_400_BAD_REQUEST)

        serializer = OCRSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = afterResponse(serializer.data, clofferId)
            return response
        else:
            logger.info("HttpResponse - BAD REQUEST(400) " + str(request.data))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def ocr_list_detail(request, pk):
    try:
        snippet = OCRInstance.objects.get(pk=pk)
    except OCRInstance.DoesNotExist:
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
Django REST framework에서는 이러한 View들의 집합인 ViewSet을 사용합니다.
ViewSet을 사용하면 View를 사용할 때보다는 덜 명확합니다.
하지만 Router에 ViewSet을 등록하면 자동으로 URL 패턴을 생성해주기 때문에 매우 편리합니다.
"""
# class OCRViewSet(viewsets.ModelViewSet):
#     queryset = OCRInstance.objects.all()
#     serializer_class = OCRSerializer

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