# -*- coding: UTF-8 -*-

import logging
from . import models
from django.conf import settings
from importlib import import_module
from django.contrib.sessions.models import Session
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class GlobalRequestMiddleware(MiddlewareMixin):
	__instance = None
	
	def __new__(cls, *args, **kwargs):
		if not cls.__instance:
			cls.__instance = object.__new__(cls)
		return cls.__instance
	#end new
	
	def process_request(self, request):
		logger.debug("GlobalRequestMiddleware.process_request")
		GlobalRequestMiddleware.__instance = request
	#end process_request
	
	@classmethod
	def getRequest(cls):
		return cls.__instance
	#end getRequest
#end - GlobalRequestMiddleware

class PreventConcurrentLoginsMiddleware(MiddlewareMixin):
	engine = import_module(settings.SESSION_ENGINE)
	
	def process_request(self, request):
		if request.user.is_authenticated:
			key_from_cookie = request.session.session_key
			if getattr(request.user, "login_limiter", None):
				session_key_in_visitor_db = request.user.login_limiter.session_key
				ip_address_in_visitor_db = request.user.login_limiter.ip_address
				ip_address = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("REMOTE_ADDR")
				if session_key_in_visitor_db != key_from_cookie and not request.user.has_perm("ako.concurrent_logins"):
					self.engine.SessionStore(session_key_in_visitor_db).delete()
					request.user.login_limiter.session_key = key_from_cookie
					request.user.login_limiter.ip_address = ip_address
					request.user.login_limiter.save()
				if ip_address_in_visitor_db != ip_address:
					logger.info("用户 {} 当前IP地址 {} 与上次IP地址 {} 不同".format(request.user.username, ip_address, ip_address_in_visitor_db))
			else:
				models.LoginLimiter.objects.create(
					 user = request.user,
					 session_key = key_from_cookie,
					 ip_address = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("REMOTE_ADDR")
				).save()
	#end process_request
#end - PreventConcurrentLoginsMiddleware
