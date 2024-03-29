import logging

from django.db import models

logger = logging.getLogger('django_info')

# Test Photo 
class Photo(models.Model):
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

# OCR Request 로그 저장
class SPOILER_LOG(models.Model):
    CLOFFER_ID    = models.IntegerField(null=False)
    REQT_DTTM     = models.CharField(max_length=14)
    DOC_TYP_CD    = models.CharField(max_length=2, null=False)
    REQTR_USER_NO = models.CharField(max_length=10, null=False)
    PRC_TYP_CD    = models.CharField(max_length=2, null=True)
    PRC_DTTM      = models.DateTimeField(null=True)
    PRC_FLG       = models.CharField(max_length=1, default='N')
    MSG_CTNT      = models.TextField(null=True)
    REG_DTTM      = models.DateTimeField(auto_now_add=True)
    RSTR_USER_NO  = models.CharField(max_length=10, null=False)
    REG_DEPT_CD   = models.CharField(max_length=10, null=False)
    REG_SYS_CD    = models.CharField(max_length=2, null=False)
    REG_PGM_NM    = models.CharField(max_length=100, null=False)

    # def save(self, *args, **kwargs):
    #     self.MSG_CTNT  = 'Receive request - CLOFFER_ID(' + str(self.CLOFFER_ID) + '), RSTR_USER_NO(' + self.RSTR_USER_NO + ')'
    #
    #     super().save(*args, **kwargs)

class DOC_TYP_WORD_LIST(models.Model):
    DOC_TYP_CD    = models.CharField(max_length=2, null=False)
    USE_FLG       = models.CharField(max_length=1, default='Y')
    ITM_STR_VLU01 = models.CharField(max_length=100)
    ITM_STR_VLU02 = models.CharField(max_length=100, null=True, blank=True)
    ITM_STR_VLU03 = models.CharField(max_length=100, null=True, blank=True)
    ITM_STR_VLU04 = models.CharField(max_length=100, null=True, blank=True)
    ITM_STR_VLU05 = models.CharField(max_length=100, null=True, blank=True)
    ITM_STR_VLU06 = models.CharField(max_length=100, null=True, blank=True)
    ITM_STR_VLU07 = models.CharField(max_length=100, null=True, blank=True)
    ITM_STR_VLU08 = models.CharField(max_length=100, null=True, blank=True)
    ITM_STR_VLU09 = models.CharField(max_length=100, null=True, blank=True)
    ITM_STR_VLU10 = models.CharField(max_length=100, null=True, blank=True)
    REG_DTTM      = models.DateTimeField(auto_now_add=True)