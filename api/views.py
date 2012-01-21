# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from gnome_developer_network.api.models import BuiltIn, Class
from django.http import HttpResponse
from django.db   import IntegrityError
import giraffe.ast

def _store_class (child, parent):

	try:
		parent_db = Class.objects.get(c_type=parent.c_type)
	except:
		parent_db = None

	obj = Class.objects.create(name=child.name,
							   c_type=child.c_type,
							   parent=parent_db,
							   namespace=child.namespace.name,
							   namespaced_name=child.namespaced_name)

	for sc in child.subclasses:
		_store_class (sc, child)

def _store_builtins (builtins):
	for bi in builtins:
		try:
			bidb = BuiltIn.objects.create (name=bi['name'], c_type=bi['c_type'])
		except:
			pass

def index(request):
	return HttpResponse("Hello world")

def parse(request):
	BuiltIn.objects.all().delete()
	_store_builtins (giraffe.ast.BUILTINS)


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
		return HttpResponse("<h1>No GObject.Object found</h1>")

	Class.objects.all().delete()
	_store_class (root, None)

	return HttpResponse("GIR to SQL transfusion completed")
