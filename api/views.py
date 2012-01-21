# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.http import HttpResponse

def index(request):
	return HttpResponse("Hello world")

def parse(request):
	return HttpResponse("Another world")
