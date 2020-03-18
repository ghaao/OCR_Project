from django.contrib import admin
from rangefilter.filter import DateRangeFilter

from .models import SPOILER_LOG


class SpoilerAdmin(admin.ModelAdmin):
    list_display = ['CLOFFER_ID', 'REQT_DTTM', 'DOC_TYP_CD', 'REQTR_USER_NO', 'PRC_DTTM', 'PRC_FLG',
                    'MSG_CTNT', 'REG_DTTM', 'RSTR_USER_NO', 'REG_DEPT_CD', 'REG_SYS_CD', 'REG_PGM_NM']
    list_filter = (('PRC_DTTM', DateRangeFilter), ('REG_DTTM', DateRangeFilter))
    search_fields = ['CLOFFER_ID']

admin.site.register(SPOILER_LOG, SpoilerAdmin)
