# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.core.exceptions import ObjectDoesNotExist
import api.models as models
from django.http import HttpResponse
from django.db   import IntegrityError
from giscanner.girparser import GIRParser
import giscanner.ast as ast

GIR_PATH="/usr/share/gir-1.0/%s.gir"

"""
AST_TYPE_MAPPINGS = {
}
"""

def _store_props(db_obj, ast_obj, ast_classes):
	""" Utility to map storage and ast properties """
	for ast_class in ast_classes:
		for prop in models.PROPERTY_MAPPINS[ast_class]:
			if getattr(ast_obj, prop) == None:
				continue
			setattr(db_obj, prop, getattr(ast_obj, prop))


def _store_member(node, parent):
	is_bitfield = isinstance(parent, models.Bitfield)
	try:
		if is_bitfield:
			db_member = models.Member.objects.get(name=node.name, bitfield=parent)
		else:
			db_member = models.Member.objects.get(name=node.name, enum=parent)
		return db_member
	except ObjectDoesNotExist:
		pass

	db_member = models.Member()
	_store_props (db_member, node, (ast.Annotated,ast.Member))

	if is_bitfield:
		db_member.bitfield = parent
	else:
		db_member.enum = parent

	db_member.save()

	return db_member

def _store_type(node):
	if isinstance(node, ast.TypeUnknown):
		model = models.TypeUnknown
		props = (ast.Type,)
	if isinstance(node, ast.Varargs):
		model = models.Varargs
		props = (ast.Type,)
	if isinstance(node, ast.Array):
		model = models.Array
		props = (ast.Type, ast.Array)
	if isinstance(node, ast.List):
		model = models.List
		props = (ast.Type, ast.List)
	if isinstance(node, ast.Map):
		model = models.Map
		props = (ast.Type,)
	else:
		model = models.Type
		props = (ast.Type,)
	
	try:
		return model.objects.get (ctype=node.ctype)
	except ObjectDoesNotExist:
		pass

	db_type = model()
	_store_props (db_type, node, props)

	if isinstance (node, ast.Array):
		db_type.array_type   = _store_type (node.array_type)
		db_type.element_type = _store_type (node.element_type)
	if isinstance(node, ast.List):
		db_type.element_type = _store_type (node.element_type)
	if isinstance(node, ast.Map):
		db_type.key_type   = _store_type (node.element_type)
		db_type.value_type = _store_type (node.element_type)

	db_type.save()
	return db_type

def _store_enum_generic (node, is_bitfield=False):
	db_ns = _store_namespace(node.namespace)

	if is_bitfield:
		model = models.Bitfield
	else:
		model = models.Enum

	try:
		db_enum = model.objects.get(namespace = db_ns, name = node.name)
		return db_enum
	except ObjectDoesNotExist:
		pass

	db_enum = model()
	db_enum.namespace = db_ns
	_store_props (db_enum, node, (ast.Annotated, ast.Node, ast.Registered))
	if is_bitfield:
		_store_props(db_enum, node, (ast.Bitfield,))
	else:
		_store_props(db_enum, node, (ast.Enum,))
	db_enum.save()

	for member in node.members:
		_store_member(member, db_enum)

	#TODO: static_methods

def _store_enum (node):
	return _store_enum_generic (node, False)

def _store_bitfield (node):
	return _store_enum_generic (node, True)

def _store_alias (node):
	db_ns = _store_namespace(node.namespace)
	try:
		db_alias = models.Alias.objects.get(namespace = db_ns, name = node.name)
		return db_alias
	except ObjectDoesNotExist:
		pass

	db_alias = models.Alias()
	db_alias.namespace = db_ns
	_store_props (db_alias, node, (ast.Annotated, ast.Node, ast.Alias))
	db_alias.target = _store_type (node.target)
	db_alias.save()
	return db_alias

def _store_node(node, db_ns):
	if isinstance(node, ast.Enum):
		_store_enum (node)
	if isinstance(node, ast.Bitfield):
		_store_bitfield (node)
	if isinstance(node, ast.Alias):
		_store_alias (node)

def _store_namespace (ns):
	try:
		db_ns = models.Namespace.objects.get(name = ns.name, version = ns.version)
		return db_ns
	except ObjectDoesNotExist:
		pass

	db_ns = models.Namespace()
	_store_props (db_ns, ns, (ast.Namespace,))
	db_ns.save()

	return db_ns

def _ns_exists (ns):
	try:
		models.Namespace.objects.get(name=ns.name, version=ns.version)
		return True
	except ObjectDoesNotExist:
		return False

def _store_parser (parser):
	_build_includes_parsers (parser)
	ns = parser.get_namespace ()
	db_ns = _store_namespace (ns)

	for item in ns:
		_store_node(ns.get (item), db_ns)

def _build_includes_parsers (parser):
	incs = parser.get_includes()
	for inc in incs:
		if _ns_exists (inc):
			continue
		path = GIR_PATH % str(inc)
		p = GIRParser()
		p.parse(path)
		_store_parser (p)

def parse(request):
	models.Namespace.objects.all().delete()

	parser = GIRParser()
	parser.parse(GIR_PATH % "Gtk-3.0")
	_store_parser(parser)

	return HttpResponse("GIR to SQL transfusion completed")

def index(request):
	page = "<h1>GLib Functions</h1><ul>"
	return HttpResponse(page)
