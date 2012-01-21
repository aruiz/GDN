# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from gnome_developer_network.api.models import BuiltIn, Class
from django.http import HttpResponse
import giraffe.ast

def _store_class (child, parent):
	obj = Class.objects.create (name=child.name, c_type=child.c_type, parent=parent)
	for sc in child.subclasses:
		_store_class (sc, obj)


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
	repo.add_gir ("/usr/share/gir-1.0/Gio-2.0.gir")
	repo.link()

	gob = None
	for ns in repo.namespaces:
		if ns.name == "GObject":
			gob = ns

	root = None
	if gob:
		for cl in gob.classes:
			if cl.name == "Object":
				root = cl

	if root == None:
		return HttpResponse("boo")

	root_db = Class.objects.create (name=root.name, c_type=root.c_type)
	for sc in root.subclasses:
		_store_class (sc, root_db)
		
	return HttpResponse("the end")
