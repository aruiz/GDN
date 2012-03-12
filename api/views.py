# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.core.exceptions import ObjectDoesNotExist
from giscanner.girparser import GIRParser
import api.models as models
from django.http import HttpResponse
from django.db   import IntegrityError

from storage import GIR_PATH, store_parser

def parse(request):
	parser = GIRParser()
	parser.parse(GIR_PATH % "Gtk-3.0")
	store_parser(parser)

	return HttpResponse("<html><head><title>GIR to SQL transfusion completed</title></head><body><h1>GIR to SQL transfusion completed</h1></body></html>")

def index(request):
	page = "<h1>GLib Functions</h1><ul>"
	return HttpResponse(page)
