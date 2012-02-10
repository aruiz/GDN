# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.core.exceptions import ObjectDoesNotExist
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

def _store_props(db_obj, ast_obj, ast_classes):
	for ast_class in ast_classes:
		for prop in models.PROPERTY_MAPPINS[ast_class]:
			if getattr(ast_obj, prop) == None:
				continue
			setattr(db_obj, prop, getattr(ast_obj, prop))

def _store_namespace (ns):
	try:
		db_ns = models.Namespace.objects.get(name = ns.name)
	#TODO: Catch the right exception for this
	except:
		db_ns = models.Namespace()

	_store_props (db_ns, ns, (ast.Namespace,))
	db_ns.save()

	return db_ns
	
def _store_type (ast_type):
	try:
		db_type = models.Type.objects.get(c_type = ast_type.c_type)
	except ObjectDoesNotExist:
		db_type = models.Type()
		_store_props (db_type, ast_type, (ast.Node, ast.Type))
		print db_type.namespace
		db_type.save()

	return db_type
	

def _store_param (param):
	db_param = models.Parameter()
	db_param.tn_type = _store_type (param.get_type())
	_store_props (db_param, param, (ast.TypedNode, ast.Parameter))
	db_param.save()

	return db_param

def _store_return_value (rvalue):
	db_rvalue = models.ReturnValue()
	_store_props (db_rvalue, rvalue, (ast.TypedNode, ast.Parameter))
	db_rvalue.tn_type = _store_type (rvalue.get_type())
	db_rvalue.save()

	return db_rvalue

def _store_function (fn):
	try:
		db_fn = models.Function.objects.get(namespaced_name = fn.namespaced_name)
	except ObjectDoesNotExist:
		db_rvalue = _store_return_value (fn.return_value)
		db_params = [_store_param(param) for param in fn.parameters]

		db_fn = models.Function(namespaced_name = fn.namespaced_name)
		_store_props (db_fn, fn, (ast.Callable, ast.Node))
		db_fn.return_value = db_rvalue
		db_fn.save()

		return db_fn

	#TODO: Update
	return db_fn

def parse(request):
	repo = ast.Repository()
	repo.add_gir ("/usr/share/gir-1.0/GLib-2.0.gir")
	repo.add_gir ("/usr/share/gir-1.0/GObject-2.0.gir")
	repo.add_gir ("/usr/share/gir-1.0/Gio-2.0.gir")
	repo.link()

	for ns in repo.namespaces:
		db_ns = _store_namespace (ns)
		for fn in ns.functions:
			_store_function (fn)
#
#	if root_class == None:
#		return HttpResponse("<h1>No GObject.Object found</h1>")

	return HttpResponse("GIR to SQL transfusion completed")
