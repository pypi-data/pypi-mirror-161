# -*- coding: UTF-8 -*-

# import datetime
# from ako import router
# from . import servicefrom django.conf import settings
# from django.utils import timezone
from django.db import models

from .services import config_service


# Create your models here.

class Configure(models.Model):
    group = models.CharField(verbose_name="分组", max_length=128, db_index=True)
    key = models.CharField(verbose_name="参数名", max_length=128, db_index=True)
    value = models.TextField(verbose_name="参数值", blank=True, default="")
    description = models.CharField(verbose_name="说明", max_length=255)

    SEO_FIELDS = ["group", "key", "value", "description"]

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        result = super().save(force_insert, force_update, using, update_fields)
        config_service.updateConfig(self.group, self.key, self.value)
        return result

    # end save

    def delete(self, using=None, keep_parents=False):
        result = super().delete(using, keep_parents)
        # utility.updateConfig()    # 完全更新缓存
        return result

    # end delete

    def value_short(self):
        if len(self.value) > 10:
            return self.value[:10] + "..."
        return self.value

    value_short.short_description = "参数值"
    value_short.admin_order_field = "value"

    # end title

    class Meta:
        db_table = 'dictionary_configure'
        verbose_name_plural = "1. 字典 - 系统配置"
        verbose_name = "配置"
        unique_together = [("group", "key")]

    # end - Meta

    def __str__(self):
        return "[{}/{}] {}".format(self.group, self.key, self.description)
    # end str
# end - Config

# def advert_image_upload_to(instance, filename):
#     now = timezone.now()
#     db = settings.DATABASE_MAPPING.get(router.getSiteDomain())
#     if db:
#         return "{}/fdbimg/{}{}.{}".format(db, now.strftime("%Y-%m-%d/%H%M%S"), abs(hash(filename)), filename[filename.rfind(".")+1:])
#     return "fdbimg/{}{}.{}".format(now.strftime("%Y-%m-%d/%H%M%S"), abs(hash(filename)), filename[filename.rfind(".")+1:])

# end - advert_image_upload_to


# class Advert(models.Model):
#     LOCATION_CHOICES = [
#         ("pre_nav", "导航条上方(最顶)"),
#         ("pre_title", "标题上方(导航条下方)"),
#         ("pre_breadcrumb", "标题下方(面包屑上方)"),
#         ("pre_footer", "页脚上方(无页脚不显示)"),
#         ("post_footer", "页脚下方(版权信息上方)"),
#         ("carousel", "首页轮播"),
#     ]
#
#     location = models.CharField(verbose_name="位置", max_length=32, choices=LOCATION_CHOICES)
#     image = models.ImageField(verbose_name="图片", upload_to=advert_image_upload_to)
#     url = models.URLField(verbose_name="链接")
#     hint = models.CharField(verbose_name="提示文本", max_length=255, blank=True)
#     expire = models.DateTimeField(verbose_name="过期时间", db_index=True)
#     sort = models.IntegerField(verbose_name="排序", help_text="从大到小", default=0, db_index=True)
#
#     SEO_FIELDS = [ "url", "hint" ]
#
#     def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
#         result = super().save(force_insert, force_update, using, update_fields)
#         # utility.updateAdvert()
#         return result
#     #end save
#
#     def title(self):
#         return str(self)
#     title.short_description = "标题"
#     #end title
#
#     class Meta:
#         verbose_name_plural = "1.图片广告"
#         verbose_name = "广告"
#     #end - Meta
#
#     def __str__(self):
#         return "广告 {} #{}".format(self.location, self.id)
#     #end str
# #end - Advert
