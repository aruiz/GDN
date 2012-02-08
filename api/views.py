# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
import gnome_developer_network.api.models as models
from django.http import HttpResponse
from django.db   import IntegrityError
import gnome_developer_network.api.giraffe.ast as ast

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

def _store_namespace (ns):
	try:
		db_ns = models.Namespace.objects.get(name = ns.name)
	#TODO: Catch the right exception for this
	except:
		db_ns = models.Namespace()

	for prop in models.PROPERTY_MAPPINS[ast.Namespace]:
		setattr(db_ns, prop, getattr(ns, prop))
	db_ns.save()


def _store_class (cl):
	parent = None
	try:
		parent = models.Class.objects.get(namespaced_name = cl.parent_class.namespaced_name)
	except:
		if cl.parent_class:
			parent = _store_class(cl.parent_class)
	
	try:
		db_class = models.Class.objects.get(namespaced_name = cl.namespaced_name)
		return db_class
	#TODO: Catch the right exception for this
	except:
		pass

	db_class = models.Class()
	db_class.name = cl.name
	db_class.namespace = cl.namespace
	db_class.parent_class = parent
	db_class.save()

	for subcl in cl.subclasses:
		_store_class (subcl)

	return db_class
	
def parse(request):
	repo = ast.Repository()
	repo.add_gir ("/usr/share/gir-1.0/GLib-2.0.gir")
	repo.add_gir ("/usr/share/gir-1.0/GObject-2.0.gir")
	repo.add_gir ("/usr/share/gir-1.0/Gio-2.0.gir")
	repo.link()

	for ns in repo.namespaces:
		_store_namespace(ns)
#		for cl in ns.classes:
#			_store_class(cl)
#
#	if root_class == None:
#		return HttpResponse("<h1>No GObject.Object found</h1>")

	return HttpResponse("GIR to SQL transfusion completed")
