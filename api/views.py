# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.core.exceptions import ObjectDoesNotExist
import gnome_developer_network.api.models as models
from django.http import HttpResponse
from django.db   import IntegrityError
from giscanner.girparser import GIRParser
import giscanner.ast as ast
"""
AST_TYPE_MAPPINGS = {
		ast.Type:       models.Type,
		ast.BaseType:    models.BaseType,
		ast.VarArgs:     models.VarArgs,
		ast.Array:       models.Array,
		ast.Enumeration: models.Enumeration,
		ast.Record:      models.Struct,
		ast.Class:       models.Class,
		ast.Interface:   models.Interface,
		ast.Callback:    models.Callback,
		ast.BitField:    models.Enumeration
}


def _store_type_generic (ast_type, db_ns):
	model = AST_TYPE_MAPPINGS[ast_type.__class__]

	if ast_type.name == "DateMonth":
		import traceback
		traceback.print_stack()
		print model
		print ast_type.__class__
		print ast_type.name

	if model == models.Enumeration:
		is_bitfield = type(ast_type) == ast.BitField
		return _store_enum (ast_type, db_ns, is_bitfield)
	if model == models.Struct:
		return _store_struct (ast_type, db_ns)
	if model == models.Class:
		return _store_class (ast_type, dn_ns)
	if model == models.Interface:
		is_interface = type(ast_type) == ast.Interface
		return _store_class (ast_type, db_ns, is_interface)

	try:
		db_type = model.objects.get(name = ast_type.name, c_type = ast_type.c_type)
	except ObjectDoesNotExist:
		db_type = model()
		db_type.namespace = db_ns
		if isinstance(db_type, models.Array):
			child_type = _store_type_generic (ast_type.child_type, db_ns)
			db_type.child_type = child_type
		_store_props (db_type, ast_type, (ast.Node, ast.Type))
		db_type.save()

	return db_type

def _store_param (param, position, db_ns, callable_obj):
	db_param = models.Parameter()
	db_param.tn_type = _store_type_generic (param.get_type(), db_ns)
	db_param.position = position
	db_param.callable_obj = callable_obj
	db_param.namespace = db_ns
	_store_props (db_param, param, (ast.TypedNode, ast.Parameter))
	db_param.save()

	return db_param

def _store_return_value (rvalue, db_ns, callable_obj):
	db_rvalue = models.ReturnValue()
	_store_props (db_rvalue, rvalue, (ast.TypedNode,))
	db_rvalue.tn_type = _store_type_generic (rvalue.get_type(), db_ns)
	db_rvalue.callable_obj = callable_obj
	db_rvalue.namespace = db_ns
	db_rvalue.save()

	return db_rvalue

def _store_generic_callable (clble, db_ns, model, asts):
	try:
		db_clble = model.objects.get(namespaced_name = clble.namespaced_name)
	except ObjectDoesNotExist:
		db_clble = model()
		_store_props (db_clble, clble, asts)
		db_clble.namespace = db_ns
		db_clble.save()

		_store_return_value (clble.return_value, db_ns, db_clble)

		pos = 0
		for param in clble.parameters:
			_store_param(param, pos, db_ns, db_clble)
			pos += 1

	#TODO: Update Callable
	return db_clble

def _store_function (fn, db_ns):
	return _store_generic_callable (fn, db_ns, models.Function, (ast.Callable, ast.Node))

def _store_callback (cb, db_ns, parent):
	try:
		db_cb = models.Callback.objects.get(namespaced_name = cb.namespaced_name)
	except ObjectDoesNotExist:
		db_cb = models.Callback()
		db_cb.namespace = db_ns
		_store_props (db_cb, cb, (ast.Node, ast.Type))
		db_cb.save()

		_store_return_value (cb.return_value, db_ns, db_cb)

		pos = 0
		for param in cb.parameters:
			_store_param(param, pos, db_ns, db_cb)
			pos += 1

	return db_cb

def _store_method (cb, db_ns, parent):
	classes = (ast.Method, ast.Callable, ast.Node)
	db_method = _store_generic_callable (cb, db_ns, models.Method, classes)
	db_method.method_of = parent
	db_method.save()

def _store_signal (sig, db_ns, parent):
	try:
		db_sig = models.Signal.objects.get(namespaced_name = sig.namespaced_name)
	except ObjectDoesNotExist:
		db_sig = models.Signal()
		db_sig.namespace = db_ns
		_store_props (db_sig, sig, (ast.Node, ast.Callable))
		db_sig.signal_of = parent
		db_sig.save()

		_store_return_value (sig.return_value, db_ns, db_sig)

		pos = 0
		for param in sig.parameters:
			_store_param(param, pos, db_ns, db_sig)
			pos += 1

	return db_sig

def _store_value (val, db_ns, parent):
	try:
		db_val = models.Value.objects.get(val = val.value, name = val.name)
	except ObjectDoesNotExist:
		db_val = models.Value()
		db_val.value_of = parent
		_store_props (db_val, val, (ast.Node,))
		db_val.val = val.value
		db_val.namespace = db_ns
		db_val.save()

	return db_val

def _store_enum (enum, db_ns, is_bitfield=False):
	try:
		db_enum = models.Enumeration.objects.get(namespaced_name = enum.namespaced_name)
	except ObjectDoesNotExist:
		db_enum = models.Enumeration()
		_store_props (db_enum, enum, (ast.Node, ast.Type))
		db_enum.is_bitfield = is_bitfield
		db_enum.namespace = db_ns
		db_enum.save()

		for member in enum.members:
			_store_value (member, db_ns, db_enum)


	return db_enum

def _store_field (field, db_ns, parent):
	try:
		db_field = models.Field.objects.get(field_of = parent, name = field.name)
	except ObjectDoesNotExist:
		db_field = models.Field()
		db_field.tn_type = _store_type_generic (field.get_type(), db_ns)
		db_field.field_of = parent
		_store_props (db_field, field, (ast.TypedNode,))
		db_field.save()

	return db_field

def _store_struct (record, db_ns):
	try:
		db_record = models.Struct.objects.get(c_type = record.c_type)
	except ObjectDoesNotExist:
		db_record = models.Record()
		_store_props (db_record, record, (ast.Node, ast.Type, ast.Record))
		db_record.namespace = db_ns
		db_record.save()

	return db_record

def _store_class (klass, db_ns, is_interface = False):
	if is_interface:
		model = models.Interface
	try:
		db_class = model.objects.get(c_type = klass.c_type)
	except ObjectDoesNotExist:
		db_class = model()
		_store_props (db_class, klass, (ast.Node, ast.Type, ast.Record, ast.Class))
		db_class.namespace = db_ns
		if not is_interface and klass.parent_class:
			parent = _store_class (klass.parent_class, db_ns)
			db_class.parent_class = parent
		db_class.save()

		for field in klass.fields:
			_store_field (field, db_ns, db_class)
		for callback in klass.callbacks:
			_store_callback (callback, db_ns, db_class)
		for method in klass.methods:
			_store_method (method, db_ns, db_class)
		for prop in klass.properties:
			_store_property (prop, db_ns, db_class)
		for signal in klass.signals:
			_store_signal (signal, db_ns, db_class)

	return db_class

def _store_property (prop, db_ns, parent):
	try:
		db_prop = models.Property.objects.get (name = prop.name, property_of = parent)
	except ObjectDoesNotExist:
		db_type = _store_type_generic (prop.get_type(), db_ns)
		db_prop = models.Property()
		db_prop.property_of = parent
		db_prop.tn_type     = db_type
		_store_props (db_prop, prop, (ast.TypedNode, ast.Property))
		db_prop.save()

	return db_prop

def _store_prerequisite (prereq, db_ns):
	if isinstance(prereq, ast.Interface):
		model = models.Interface
	elif isinstance(prereq, ast.Class):
		model = models.Class
	else:
		print "Couldn't figure out a suitable type for the prerequisite %s for interface %s" % (prereq, iface.namespaced_name)
		return None

	try:
		db_prereq = model.objects.get(namespaced_name = prereq.namespaced_name)
	except ObjectDoesNotExist:
		db_prereq = _store_class (prereq, db_ns, model == ast.Interface)

		if model == models.Interface:
			for _prereq in prereq.prerequisites:
				_store_prerequisite (_prereq, db_ns)
		else:
			for iface in prereq.interfaces:
				try:
					db_iface = models.Interface.objects.get(namespaced_name = iface.namespaced_name)
					db_prereq.interfaces.add(db_iface)
				except ObjectDoesNotExist:
					info = (iface.namespaced_name, prereq.namespaced_name)
					print "Couldn't find interface %s implemented by %s", info
					continue			

	return db_prereq
"""

def _store_props(db_obj, ast_obj, ast_classes):
	for ast_class in ast_classes:
		for prop in models.PROPERTY_MAPPINS[ast_class]:
			if getattr(ast_obj, prop) == None:
				continue
			setattr(db_obj, prop, getattr(ast_obj, prop))

def _store_namespace (ns):
	try:
		db_ns = models.Namespace.objects.get(name = ns.name, version = ns.version)
		return db_ns
	except ObjectDoesNotExist:
		db_ns = models.Namespace()
		_store_props (db_ns, ns, (ast.Namespace,))
		db_ns.save()
		return db_ns

def parse(request):
	parser = GIRParser()
	parser.parse("/usr/share/gir-1.0/Gtk-3.0.gir")
	namespaces = [_store_namespace(parser.get_namespace()),]
	for ns in parser.get_includes():
		namespaces.append(_store_namespace (ns))

	return HttpResponse("GIR to SQL transfusion completed")

def index(request):
	page = "<h1>GLib Functions</h1><ul>"
	return HttpResponse(page)
