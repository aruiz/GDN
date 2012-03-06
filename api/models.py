# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.db import models
import giscanner.ast as ast

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
	ast.Type:       ('ctype','gtype_name','origin_symbol','target_giname','is_const','resolved', 'target_foreign', 'target_fundamental'),
	ast.Array:      ('array_type', 'zeroterminated','length_param_name','size'),
	ast.List:       ('name',),
	ast.Callable:   ('throws',),
	ast.Function:   ('is_method','is_constructor','shadowed_by','shadows','moved_to','symbol'),
	ast.Callback:   ('ctype',),
	ast.TypeContainer: ('transfer',),
	ast.Parameter:  ('argname', 'direction', 'allow_none', 'closure_name', 'destroy_name'),
	ast.Compound:   ('ctype', 'c_symbol_prefix', 'disguised'),
	ast.Field:      ('name','readable','writable','private','bits'),
	ast.Class:      ('ctype', 'c_symbol_prefix', 'fundamental', 'is_abstract'),
	ast.Signal:     ('when', 'no_recurse', 'detailed', 'action', 'no_hooks'),
	ast.Property:   ('readable', 'writable', 'construct_only', 'transfer', 'construct'),
	ast.Interface:  ('ctype', 'c_symbol_prefix'),
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
	#unresolved_string = models.CharField (max_length = CF_MAX_LENGTH)
	target_foreign = models.CharField (max_length = CF_MAX_LENGTH, null=True)
	target_fundamental = models.CharField (max_length = CF_MAX_LENGTH, null=True)
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
	array_type = models.CharField(max_length=CF_MAX_LENGTH)
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
		return self.name

class Registered(models.Model):
	gtype_name = models.CharField (max_length = CF_MAX_LENGTH)
	#TODO
#	get_type = get_type

class Callable(Node):
	throws = models.BooleanField(default=False)
	instance_parameter = models.IntegerField ()
	retval = models.ForeignKey('Return', related_name='clble_retval')

class Function(Callable):
	is_method      = models.BooleanField(default=False)
	is_constructor = models.BooleanField(default=False)
	shadowed_by    = models.CharField(max_length=CF_MAX_LENGTH)
	shadows        = models.CharField(max_length=CF_MAX_LENGTH)
	moved_to       = models.CharField(max_length=CF_MAX_LENGTH)
	symbol         = models.CharField(max_length=CF_MAX_LENGTH)

class FunctionParameter (models.Model):
	function = models.ForeignKey('Function')
	parameter = models.ForeignKey('Parameter')
	position = models.IntegerField ()

class ErrorQuarkFunction(Function):
	error_domain = models.CharField(max_length=CF_MAX_LENGTH)

class VFunction(Callable):
	pass

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
	scope = scope = models.CharField(max_length=CF_MAX_LENGTH)
	caller_allocates = models.BooleanField(default=False)

class Return(TypeContainer):
	pass

class Enum(Node, Registered):
	c_symbol_prefix = models.CharField(max_length=CF_MAX_LENGTH)
	ctype           = models.CharField(max_length=CF_MAX_LENGTH)
	error_domain    = models.CharField(max_length=CF_MAX_LENGTH)
	static_methods  = models.ManyToManyField('Function')
	members         = models.ManyToManyField('Member')

class Bitfield(Node, Registered):
	ctype           = models.CharField(max_length=CF_MAX_LENGTH)
	c_symbol_prefix = models.CharField(max_length=CF_MAX_LENGTH)
	members         = models.ManyToManyField('Member')
	static_methods  = models.ManyToManyField('Function')

class Member(Annotated):
	name = models.CharField(max_length=CF_MAX_LENGTH)
	symbol = models.CharField(max_length=CF_MAX_LENGTH)
	nick = models.CharField(max_length=CF_MAX_LENGTH)
	value = models.CharField(max_length=CF_MAX_LENGTH)

class Compound(Node, Registered):
	ctype = models.CharField(max_length=CF_MAX_LENGTH)
	c_symbol_prefix = models.CharField(max_length=CF_MAX_LENGTH)
	disguised       = models.BooleanField(default=False)
	methods         = models.ManyToManyField('Function', related_name='cmp_methods')
	static_methods  = models.ManyToManyField('Function', related_name='cmp_static_methods')
	constructors    = models.ManyToManyField('Function', related_name='cmp_constructors')
	fields          = models.ManyToManyField('Field', related_name='cmp_fields')
	#get_type = get_type	

class Field(Annotated):
	name = models.CharField(max_length=CF_MAX_LENGTH)
	readable = models.BooleanField(default=False)
	writable = models.BooleanField(default=False)
	private = models.BooleanField(default=False)
	bits = models.CharField(max_length=CF_MAX_LENGTH)
	type = models.ForeignKey('Type', null=True)
	anonymous_node = models.ForeignKey('Callback', null=True)

	def __unicode__ (self):
		return self.name

class Record(Compound):
	is_gtype_struct_for = models.ForeignKey('Type', null=True)

class Union(Compound):
	pass

class Boxed(Node, Registered):
	c_symbol_prefix = models.CharField(max_length=CF_MAX_LENGTH)
	constructors    = models.ManyToManyField('Function', related_name='bxd_constructors')
	methods         = models.ManyToManyField('Function', related_name='bxd_methods')
	static_methods  = models.ManyToManyField('Function', related_name='bxd_static_methods')

class Signal(Callable):
	when = models.CharField(max_length=20)
	no_recurse = models.BooleanField(default=False)
	detailed = models.BooleanField(default=False)
	action = models.BooleanField(default=False)
	no_hooks = models.BooleanField(default=False)

class SignalParameter(models.Model):
	signal    = models.ForeignKey('Signal')
	parameter = models.ForeignKey('Parameter')
	position  = models.IntegerField()

class Class(Node, Registered):
	ctype = models.CharField(max_length=CF_MAX_LENGTH)
	c_symbol_prefix = models.CharField(max_length=CF_MAX_LENGTH)
	fundamental = models.BooleanField(default=False)
	is_abstract = models.BooleanField(default=False)
	parent         = models.ForeignKey('Type',    null=True, related_name='cls_parent')
	unref_func     = models.ForeignKey('Function', null=True, related_name='cls_unref')
	ref_func       = models.ForeignKey('Function', null=True, related_name='cls_ref')
	set_value_func = models.ForeignKey('Function', null=True, related_name='cls_set_value')
	get_value_func = models.ForeignKey('Function', null=True, related_name='cls_get_value')

	glib_type_struct = models.ForeignKey('Type', null=True)

	methods         = models.ManyToManyField('Function', related_name='cls_methods')
	virtual_methos  = models.ManyToManyField('Function', related_name='cls_vmethods')
	static_methods  = models.ManyToManyField('Function', related_name='cls_smethods')
	constructors    = models.ManyToManyField('Function', related_name='cls_constructors')
	signals         = models.ManyToManyField('Signal', related_name='cls_signals')
	interfaces      = models.ManyToManyField('Interface', related_name='cls_ifaces')

	fields          = models.ManyToManyField('Field', related_name='cls_fields')
	properties      = models.ManyToManyField('Property', related_name='cls_props')
	#parent_chain = []

class Interface(Node, Registered):
	ctype = models.CharField(max_length=CF_MAX_LENGTH)
	c_symbol_prefix = models.CharField(max_length=CF_MAX_LENGTH)

	methods         = models.ManyToManyField('Function', related_name='iface_methods')
	virtual_methos  = models.ManyToManyField('Function', related_name='iface_vmethods')
	static_methods  = models.ManyToManyField('Function', related_name='iface_smethods')
	constructors    = models.ManyToManyField('Function', related_name='iface_constructors')
	signals         = models.ManyToManyField('Signal', related_name='iface_signals')

	fields          = models.ManyToManyField('Field', related_name='iface_fields')
	properties      = models.ManyToManyField('Property', related_name='iface_props')

	prerequisites = models.ManyToManyField('Type', related_name='iface_prereq')
	glib_type_struct = models.ForeignKey('Type', null=True, related_name='iface_glib_type_struct')
	#parent_chain = []

class Constant(Node):
	ctype = models.CharField(max_length=CF_MAX_LENGTH)
	value = models.CharField(max_length=CF_MAX_LENGTH)
	value_type = models.ForeignKey('Type')

class Property(Node):
	readable       = models.BooleanField(default=False)
	writable       = models.BooleanField(default=False)
	construct_only = models.BooleanField(default=False)
	transfer       = models.CharField(max_length=20)
	construct      = models.BooleanField(default=False)
	type = models.ForeignKey('Type')

class Callback(Callable):
	ctype = models.CharField(max_length=CF_MAX_LENGTH, null=True)

class CallbackParameter (models.Model):
	callback = models.ForeignKey('Callback')
	parameter = models.ForeignKey('Parameter')
	position = models.IntegerField ()
