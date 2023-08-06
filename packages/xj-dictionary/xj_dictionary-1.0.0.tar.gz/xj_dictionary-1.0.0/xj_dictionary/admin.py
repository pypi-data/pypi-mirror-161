# -*- coding: UTF-8 -*-

# from ako import router
# from . import models, forms
from django.contrib import admin

from . import models

@admin.register(models.Configure)
class ConfigureAdmin(admin.ModelAdmin):
    fields = ["group", "description", "key",  "value"]
    
    # fieldsets = [
    #     (None, {
    #         "fields": ["group", "description", "key", "value", ],
    #     }),
    # ]
    
    list_display = ["description", "group", "key", "value_short"]
    list_filter = ["group"]
    
    def get_form(self, request, obj=None, **kwargs):
        # if not router.isMobile(request):
        #     kwargs["form"] = forms.py.ConfigAdminForm
        
        return super().get_form(obj, **kwargs)
    #end get_form
#end - ConfigAdmin

# @admin.register(models.Advert)
# class AdvertAdmin(admin.ModelAdmin):
#     fieldsets = [
#         (None, {
#             "fields" : ["location", "image", "url", "hint", "expire", "sort"],
#         }),
#     ]
#
#     list_display = [ "title", "hintShort", "expire", "location", "sort" ]
#     list_filter = [ "location" ]
#
#     def hintShort(self, obj):
#         if len(obj.hint) > 32:
#             return obj.hint[:32] + "..."
#         return obj.hint
#     hintShort.short_description = "文本"
#     #end hintShort
# #end - AdvertAdmin

admin.site.site_header = 'msa一体化管理后台'
admin.site.site_title = 'msa一体化管理后台'
