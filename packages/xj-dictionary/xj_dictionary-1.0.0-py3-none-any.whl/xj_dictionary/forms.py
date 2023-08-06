# -*- coding: UTF-8 -*-

from . import models
from django import forms
# from mdeditor.fields import MDTextFormField

class ConfigAdminForm(forms.ModelForm):
	class Meta:
		models = models.Configure
		fields = [ "group", "key", "value", "description" ]
	#end - Meta
	
	# value = MDTextFormField(label="参数值")
#end - ConfigAdminForm
