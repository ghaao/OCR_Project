from django.contrib import admin
from rangefilter.filter import DateRangeFilter

from .models import *

class SpoilerAdmin(admin.ModelAdmin):
    list_display = ['CLOFFER_ID', 'REQT_DTTM', 'DOC_TYP_CD', 'REQTR_USER_NO', 'PRC_TYP_CD', 'PRC_DTTM', 'PRC_FLG',
                    'MSG_CTNT', 'REG_DTTM', 'RSTR_USER_NO', 'REG_DEPT_CD', 'REG_SYS_CD', 'REG_PGM_NM']
    list_filter = (('PRC_DTTM', DateRangeFilter), ('REG_DTTM', DateRangeFilter))
    search_fields = ['CLOFFER_ID']

class DocTypWordListAdmin(admin.ModelAdmin):
    list_display  = ['DOC_TYP_CD', 'USE_FLG', 'ITM_STR_VLU01', 'ITM_STR_VLU02', 'ITM_STR_VLU03', 'ITM_STR_VLU04', 'ITM_STR_VLU05',
                    'ITM_STR_VLU06', 'ITM_STR_VLU07', 'ITM_STR_VLU08', 'ITM_STR_VLU09', 'ITM_STR_VLU10', 'REG_DTTM']
    search_fields = ['DOC_TYP_CD']

admin.site.register(SPOILER_LOG, SpoilerAdmin)
admin.site.register(Photo)
admin.site.register(DOC_TYP_WORD_LIST, DocTypWordListAdmin)
