from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers

from config import settings
from ocr_app import views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('tesseract/', views.ocr_list),
    path('tesseract/<int:pk>', views.ocr_list_detail),
]

urlpatterns = format_suffix_patterns(urlpatterns)

"""
REST Framework에서는 URL에 따라 다른 로직이 실행될 수 있도록 자동으로 라우팅하는 기능을 제공합니다.
Router에서는 사용자의 요청을 확인하고 어디에서 이 요청이 처리되어야 하는지 알려줍니다.
"""
# router = routers.DefaultRouter()
# router.register(r'tesseract', views.OCRViewSet)
#
# urlpatterns = [
#     url(r'^', include(router.urls)),
#     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)