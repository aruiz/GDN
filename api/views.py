# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from gnome_developer_network.api.models import BuiltIn, Class, Interface
from django.http import HttpResponse
from django.db   import IntegrityError
import giraffe.ast

def _store_interface (child):
	#TODO: Handle interface parent

	
	obj = Interface.objects.create(name=child.name,
	                               c_type=child.c_type,
	                               namespace=child.namespace.name,
	                               namespaced_name=child.namespaced_name)


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
	BuiltIn.objects.all().delete()
	for bi in builtins:
		bidb = BuiltIn.objects.create (name=bi['name'], c_type=bi['c_type'])

def index(request):
	page = "<h1>Classes</h1><ul>"
	for cl in Class.objects.all():
		page += "<li>%s</li>" % cl.namespaced_name
	page +="</ul>"

	page += "<h1>Built-in types</h1><ul>"
	for cl in BuiltIn.objects.all():
		page += "<li>%s</li>" % cl.c_type
	page +="</ul>"

	return HttpResponse(page)

def parse(request):
	_store_builtins (giraffe.ast.BUILTINS)


	repo = giraffe.ast.Repository()
	repo.add_gir ("/usr/share/gir-1.0/GLib-2.0.gir")
	repo.add_gir ("/usr/share/gir-1.0/GObject-2.0.gir")
	repo.add_gir ("/usr/share/gir-1.0/Gio-2.0.gir")
	repo.link()

	Class.objects.all().delete()
	Interface.objects.all().delete()
	BuiltIn.objects.all().delete()

	gob = None
	for ns in repo.namespaces:
		if ns.name == "GObject":
			gob = ns
		for intfc in ns.interfaces:
			_store_interface (intfc)

	root_class = None
	if gob:
		for cl in gob.classes:
			if cl.name == "Object":
				root_class = cl

	if root_class == None:
		return HttpResponse("<h1>No GObject.Object found</h1>")


	_store_class (root_class, None)

	return HttpResponse("GIR to SQL transfusion completed")
