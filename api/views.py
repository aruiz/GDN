# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from gnome_developer_network.api.models import BuiltIn, Class
from django.http import HttpResponse
import giraffe.ast

def index(request):
	return HttpResponse("Hello world")

def parse(request):
	for bi in giraffe.ast.BUILTINS:
		try:
			bidb = BuiltIn.objects.create (name=bi['name'], c_type=bi['c_type'])
		except:
			pass

	repo = giraffe.ast.Repository()
	repo.add_gir ("/usr/share/gir-1.0/GLib-2.0.gir")
	repo.add_gir ("/usr/share/gir-1.0/GObject-2.0.gir")
	repo.link()

	output = ""
	for ns in repo.namespaces:
		output += "<h1>%s</h1>" % ns.name 
		for cl in ns.classes:
			output += ns.name + "." + cl.name + " <br/>"

	return HttpResponse(output)
