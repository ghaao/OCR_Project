#Serializer는 Model로부터 가져온 데이터베이스의 데이터들을 JSON이나 XML같은 형식으로 쉽게 변환할 수 있게 해줍니다.
#Serializer는 또한 JSON이나 XML같은 형태의 데이터를 Model형태의 데이터로 변경하는 Deserializing 기능도 제공합니다.

#앞서 생성한 모델을 가져옵니다. from [app이름].models import [Model 이름]으로 가져옵니다
from ocr_app.models import OCRInstance
from rest_framework import serializers

class OCRSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        # model의 이름을 적어줍니다.
        model = OCRInstance
        # fileds에는 Model에서 추출할 필드명들을 반드시 리스트 형태로 적어줍니다.
        fields = ('CLOFFER_ID', 'MSG_CTNT', 'RSTR_USER_NO', 'REG_DEPT_CD')