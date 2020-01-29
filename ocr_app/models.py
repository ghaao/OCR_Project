from django.db import models
from django.utils import timezone
import logging
logger = logging.getLogger('django_info')

class OCRInstance(models.Model):
    CLOFFER_ID   = models.IntegerField(null=False)
    REQT_DTTM    = models.DateTimeField()
    MSG_CTNT     = models.CharField(max_length=4000, null=True)
    CHG_DTTM     = models.DateTimeField()
    REG_DTTM     = models.DateTimeField()
    RSTR_USER_NO = models.CharField(max_length=10)
    REG_DEPT_CD  = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        # Time configuration
        self.REQT_DTTM = timezone.localtime()
        self.CHG_DTTM  = timezone.localtime()
        self.REG_DTTM  = timezone.localtime()
        self.MSG_CTNT  = 'Request - CLOFFER_ID(' + str(self.CLOFFER_ID) + '), RSTR_USER_NO(' + self.RSTR_USER_NO + ')'

        # Request 로그 저장 및 파일 기록
        super().save(*args, **kwargs)
        logger.info(self.MSG_CTNT)