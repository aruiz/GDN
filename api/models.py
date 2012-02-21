# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.db import models
import giscanner.ast as ast

""" We need to replicate each class of the AST's properties, we use this dict to automate the process. """
"""
PROPERTY_MAPPINS = {
	ast.Namespace:   ('name', 'doc', 'symbol_prefix', 'identifier_prefixes'),
	ast.Node:        ('name', 'namespaced_name', 'doc'),
	ast.Parameter:   ('is_out',),
	ast.Type:        ('is_array', 'c_type'),
	ast.Value:       ('value',),
	ast.Callable:    ('c_identifier',),
	ast.Method:      ('virtual', 'static'),
	ast.Record:      ('disguised',),
	ast.TypedNode:   ('name', 'doc', 'is_pointer', 'is_array'),
	ast.Property:    ('writable', 'construct_only'),
	ast.Class:       ('is_abstract',)
}

class Namespace(models.Model):
	name                = models.CharField(max_length=500)
	doc                 = models.TextField (null=True, blank=True)
	symbol_prefix       = models.CharField(max_length=500)
	identifier_prefixes = models.CharField(max_length=500)

	def __unicode__(self):
		return self.name

class Node(models.Model):
	name            = models.CharField(max_length=500)
	namespaced_name = models.CharField(max_length=500)
	namespace       = models.ForeignKey('Namespace', null=True, blank=True)
	doc             = models.TextField (null=True, blank=True)

	def __unicode__(self):
		return self.name

class TypedNode(models.Model):
	name       = models.CharField(max_length=500)
	doc        = models.TextField (null=True, blank=True)
	tn_type    = models.ForeignKey('Type')
	is_pointer = models.BooleanField(default=False)
	is_array   = models.BooleanField(default=False)

	def __unicode__(self):
		return self.name

class Value(Node):
	value_of = models.ForeignKey('Enumeration', null=True, blank=True)
	val      = models.CharField(max_length=500)

class Parameter(TypedNode):
	is_out       = models.BooleanField(default=False)
	position     = models.IntegerField()
	callable_obj = models.ForeignKey('Callable')

class ReturnValue(TypedNode):
	callable_obj = models.ForeignKey('Callable')
	def __unicode__(self):
		c_id = None

		if hasattr(self.callable_obj, 'c_identifier'):
			c_id = self.callable_obj.c_identifier
		else:
			hasattr(self.callable_obj, 'c_type')

		return "%s(...) -> %s" % (c_id, self.tn_type)

class Type(Node):
	is_array = models.BooleanField(default=False)
	c_type   = models.CharField(max_length=500)

class BaseType(Type):
	pass

class VarArgs(Type):
	pass

class Array(Type):
	child_type = models.ForeignKey('Type', related_name='array_child_type')
	
class Callable(Node):
	pass

class CallableId(Callable):
	c_identifier = models.CharField(max_length=500)

class Function(CallableId):
	pass

class Constructor(CallableId):
	#TODO: Can a constructor be static? 
	constructor_of = models.ForeignKey('Class')

class Enumeration(Type):
	is_bitfield = models.BooleanField(default=False)

class Record(Type):
	disguised = models.BooleanField(default=False)

class Struct(Record):
	pass

class Method(CallableId):
	method_of      = models.ForeignKey('Record', null=True)
	virtual        = models.BooleanField(default=False)
	static         = models.BooleanField(default=False)

class Field (TypedNode):
	field_of = models.ForeignKey('Record')

class Callback(Callable, Type):
	callback_of = models.ForeignKey('Record', null=True)

class Class(Record):
	parent_class = models.ForeignKey     ('self',        null=True, blank=True)
	interfaces   = models.ManyToManyField('Interface',   null=True, blank=True, related_name='class_interfaces')
	is_abstract  = models.BooleanField(default=False)

class Property(TypedNode):
	property_of    = models.ForeignKey('Class', null=True)
	writable       = models.BooleanField(default=False)
	construct_only = models.BooleanField(default=False)

class Signal(Callable):
	c_identifier = models.CharField(max_length=500)
	signal_of = models.ForeignKey('Class', null=True)

class Interface(Class):
	prerequisites = models.ManyToManyField('Record', null=True, blank=True)
"""

CF_MAX_LENGTH = 500
CF_VERSION_MAX_LENGTH = 20

PROPERTY_MAPPINS = {
	ast.Namespace:  ('name', 'version'),
	ast.Annotated:  ('version','skip','introspectable','deprecated_version','doc'),
	ast.Node:       ('c_name','gi_name','name','foreign'),
	ast.Registered: ('gtype_name',),
	ast.Enum:       ('c_symbol_prefix','ctype','error_domain'),
	ast.Bitfield:   ('c_symbol_prefix','ctype'),
	ast.Member:     ('name', 'symbol', 'nick', 'value'),
	ast.Alias:      ('ctype',),
	ast.Type:       ('ctype','gtype_name','origin_symbol','target_giname','is_const','resolved', 'unresolved_string'),
	ast.Array:      ('zeroterminated','length_param_name','size'),
	ast.List:       ('name',),
	
}

class Namespace(models.Model):
	name = models.CharField (max_length = CF_MAX_LENGTH)
	version = models.CharField (max_length = CF_MAX_LENGTH)
	#TODO:
	#From the parser:
	#c includes
	#c prefix
	#shared libraries?
	#pkg-config packages
	#doc????
	def __unicode__ (self):
		return "%s-%s" % (self.name, self.version)

class Type(models.Model):
	ctype = models.CharField (max_length = CF_MAX_LENGTH)
	gtype_name = models.CharField (max_length = CF_MAX_LENGTH)
	origin_symbol = models.CharField (max_length = CF_MAX_LENGTH)
	target_giname = models.CharField (max_length = CF_MAX_LENGTH)
	is_const = models.BooleanField(default=False)
	resolved = models.BooleanField(default=False)
	unresolved_string = models.CharField (max_length = CF_MAX_LENGTH)
	#TODO
	#target_foreign = target_foreign
	#target_fundamental = target_fundamental
	def __unicode__ (self):
		return self.ctype

class TypeUnknown(Type):
	pass

class Varargs(Type):
	pass

class Array(Type):
	zeroterminated = models.BooleanField(default=False)
	length_param_name = models.CharField(max_length=CF_MAX_LENGTH)
	size = models.IntegerField()
	array_type = models.ForeignKey('Type', related_name='array_type_rn')
	element_type = models.ForeignKey('Type', related_name='array_element_type_rn')

class List(Type):
	name = 	models.CharField(max_length=CF_MAX_LENGTH)
	element_type = models.ForeignKey('Type', related_name='list_element_type_rn')

class Map(Type):
	key_type =  models.ForeignKey('Type', related_name='key_type_rn')
	value_type =  models.ForeignKey('Type', related_name='value_type_rn')

class Include(models.Model):
	name = models.CharField(max_length=CF_MAX_LENGTH)
	version = models.CharField(max_length=CF_VERSION_MAX_LENGTH)

class Annotated(models.Model):
	version = models.CharField(max_length=CF_VERSION_MAX_LENGTH)
	skip = models.BooleanField(default=False)
	introspectable = models.BooleanField(default=False)
	deprecated_version = models.CharField(max_length=CF_VERSION_MAX_LENGTH)
	doc = models.TextField(null=True, blank=True)
	deprecated = models.CharField(max_length=CF_MAX_LENGTH)
	deprecated_version = models.CharField(max_length=CF_VERSION_MAX_LENGTH)
	#TODO
	#attributes = [] # (key, value)*

class Node(Annotated):
	c_name = models.CharField (max_length = CF_MAX_LENGTH)
	gi_name = models.CharField (max_length = CF_MAX_LENGTH)
	namespace = models.ForeignKey('Namespace')
	name = models.CharField (max_length = CF_MAX_LENGTH)
	foreign = models.BooleanField(default=False)
	#TODO
	#file_positions = set()
	def __unicode__ (self):
		return self.gi_name

class Registered(models.Model):
	gtype_name = models.CharField (max_length = CF_MAX_LENGTH)
	#TODO
#	get_type = get_type

class Callable(Node):
	throws = models.BooleanField(default=False)
	instance_parameter = models.ForeignKey('Parameter')
	#TODO
	#	retval = retval
	#	parameters = parameters

class Function(Callable):
	is_method = models.BooleanField(default=False)
	is_constructor = models.BooleanField(default=False)
	shadowed_by = models.CharField(max_length=CF_MAX_LENGTH)
	shadows = models.CharField(max_length=CF_MAX_LENGTH)
	moved_to = models.CharField(max_length=CF_MAX_LENGTH)
	#TODO
	#	symbol = symbol

class ErrorQuarkFunction(Function):
	error_domain = models.CharField(max_length=CF_MAX_LENGTH)

class VFunction(Callable):
	pass
	#TODO
	#	invoker = None

class Alias(Node):
	target = models.ForeignKey('Type')
	ctype = models.CharField(max_length=CF_MAX_LENGTH)

class TypeContainer(Annotated):
	transfer = models.CharField(max_length=CF_MAX_LENGTH)
	type     = models.ForeignKey('Type')

class Parameter(TypeContainer):
	argname      = models.CharField(max_length=CF_MAX_LENGTH)
	direction    = models.CharField(max_length=CF_MAX_LENGTH)
	allow_none   = models.BooleanField(default=False)
	closure_name = models.CharField(max_length=CF_MAX_LENGTH)
	destroy_name = models.CharField(max_length=CF_MAX_LENGTH)
	#TODO
	#	scope = scope
	#	caller_allocates = caller_allocates

class Return(TypeContainer):
	pass

class Enum(Node, Registered):
	c_symbol_prefix = models.CharField(max_length=CF_MAX_LENGTH)
	ctype = models.CharField(max_length=CF_MAX_LENGTH)
	error_domain = models.CharField(max_length=CF_MAX_LENGTH)
	#TODO
	#	static_methods = []
	#	members = members

class Bitfield(Node, Registered):
	ctype = models.CharField(max_length=CF_MAX_LENGTH)
	c_symbol_prefix = models.CharField(max_length=CF_MAX_LENGTH)
	#TODO
	# members = members
	# self.static_methods = []

class Member(Annotated):
	name = models.CharField(max_length=CF_MAX_LENGTH)
	symbol = models.CharField(max_length=CF_MAX_LENGTH)
	nick = models.CharField(max_length=CF_MAX_LENGTH)
	value = models.CharField(max_length=CF_MAX_LENGTH)
	
	enum = models.ForeignKey('Enum', null=True)
	bitfield = models.ForeignKey('Bitfield', null=True)

class Compound(Node, Registered):
	ctype = models.CharField(max_length=CF_MAX_LENGTH)
	c_symbol_prefix = models.CharField(max_length=CF_MAX_LENGTH)
	#TODO:
	#	methods = []
	#	disguised = disguised
	#	get_type = get_type	
	#	static_methods = []
	#	fields = []
	#	constructors = []

class Field(Annotated):
	name = models.CharField(max_length=CF_MAX_LENGTH)
	readable = models.BooleanField(default=False)
	writable = models.BooleanField(default=False)
	private = models.BooleanField(default=False)
	#TODO
	#	type = typenode
	#	bits = bits
	#	anonymous_node = anonymous_node

class Record(Compound):
	#TODO
	#is_gtype_struct_for = None
	pass

class Union(Compound):
	pass

class Boxed(Node, Registered):
	c_symbol_prefix = models.CharField(max_length=CF_MAX_LENGTH)
	#TODO
	#        self.constructors = []
	#        self.methods = []
	#        self.static_methods = []

class Signal(Callable):
	when = models.CharField(max_length=20)
	#TODO
	#	no_recurse = no_recurse
	#	detailed = detailed
	#	action = action
	#	no_hooks = no_hooks

class Class(Node, Registered):
	ctype = models.CharField(max_length=CF_MAX_LENGTH)
	c_symbol_prefix = models.CharField(max_length=CF_MAX_LENGTH)
	fundamental = models.BooleanField(default=False)
	is_abstract = models.BooleanField(default=False)
	#TODO
	#	parent = parent
	#	unref_func = None
	#	ref_func = None
	#	set_value_func = None
	#	get_value_func = None

	#	self.glib_type_struct = None
		# if there are 'hidden' parents
		#        self.parent_chain = []

	#        self.methods = []
	#        self.virtual_methods = []
	#        self.static_methods = []
	#        self.interfaces = []
	#        self.constructors = []
	#        self.properties = []
	#        self.fields = []
	#        self.signals = []


class Interface(Node, Registered):
	ctype = models.CharField(max_length=CF_MAX_LENGTH)
	c_symbol_prefix = models.CharField(max_length=CF_MAX_LENGTH)
	#TODO
	#	parent
	#	glib_type_struct = None
	#        parent_chain = []
	#        self.methods = []
	#        self.signals = []
	#        self.static_methods = []
	#        self.virtual_methods = []
	#        self.properties = []
	#        self.fields = []
	#        self.prerequisites = []


class Constant(Node):
	ctype = models.CharField(max_length=CF_MAX_LENGTH)
	#TODO
	#	value_type = value_type
	#	value = value

class Property(Node):
	readable = models.BooleanField(default=False)
	writable = models.BooleanField(default=False)
	construct_only = models.BooleanField(default=False)
	transfer = models.CharField(max_length=20)
	#TODO
	#	type = typeobj
	#	construct = construct

class Callback(Callable):
	ctype = models.CharField(max_length=CF_MAX_LENGTH, null=True)
