# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
	url("$^", "api.views.index"),
	)
