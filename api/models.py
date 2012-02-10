# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.db import models
import gnome_developer_network.api.giraffe.ast as ast

""" We need to replicate each class of the AST's properties, we use this dict to automate the process. """
PROPERTY_MAPPINS = {
	ast.Namespace:   ('name', 'doc', 'symbol_prefix', 'identifier_prefixes'),
	ast.Node:        ('name', 'namespaced_name', 'doc'),
	ast.Parameter:   ('is_out',),
	ast.Type:        ('is_array', 'c_type'),
	ast.Array:       ('child_type',),
	ast.Callable:    ('c_identifier',),
	ast.Method:      ('virtual', 'static'),
	ast.Enumeration: ('members',),
	ast.Record:      ('disguised', 'fields', 'callbacks', 'methods'),
	ast.TypedNode:   ('name', 'doc', 'is_pointer', 'is_array'),
	ast.Property:    ('writable', 'construct_only'),
	ast.Class:       ('constructors', 'properties', 'signals', 'parent_class', 'interfaces', 'is_abstract')
}

class Namespace(models.Model): 
	name                = models.CharField(max_length=500)
	doc                 = models.TextField (null=True, blank=True)
	symbol_prefix       = models.CharField(max_length=500)
	identifier_prefixes = models.CharField(max_length=500)

class Node(models.Model):
	name            = models.CharField(max_length=500)
	namespaced_name = models.CharField(max_length=500)
	namespace       = models.ForeignKey('Namespace', null=True, blank=True)
	doc             = models.TextField (null=True, blank=True)

class TypedNode(models.Model):
	name       = models.CharField(max_length=500)
	doc        = models.TextField (null=True, blank=True)
	tn_type    = models.ForeignKey('Type')
	is_pointer = models.BooleanField(default=False)
	is_array   = models.BooleanField(default=False)

class Value(Node):
	pass

class Parameter(TypedNode):
	is_out = models.BooleanField(default=False)

#TODO: How come a return value has "is_out" wtf?
class ReturnValue(Parameter):
	pass

class Type(Node):
	is_array = models.BooleanField(default=False)
	c_type   = models.CharField(max_length=500, unique=True)

class BaseType(Type):
	pass

class VarArgs(Type):
	pass

class Array(Type):
	child_type = models.ManyToManyField('Type', related_name='array_child_type')
	
class Callable(Node):
	parameters = models.ManyToManyField('Parameter')
	return_value = models.ForeignKey('ReturnValue', related_name='callable_return_value')
	c_identifier = models.CharField(max_length=500, unique=True)

class Function(Callable):
	pass

class Callback(Type, Callable):
	pass

class Signal(Callable):
	pass

class Method(Callable):
	virtual = models.BooleanField(default=False)
	static  = models.BooleanField(default=False)

class Constructor(Method):
	pass

class Enumeration(Type):
	members = models.ManyToManyField('Value')

class BitField(Enumeration):
	pass

class Record(Type):
	disguised = models.BooleanField(default=False)
	fields    = models.ManyToManyField('Field')
	callbacks = models.ManyToManyField('Callback')
	methods   = models.ManyToManyField('Method')

class Field (Node):
	pass

class Property(Field):
	writable       = models.BooleanField(default=False)
	construct_only = models.BooleanField(default=False)

class Class(Record):
	constructors = models.ManyToManyField('Constructor', null=True, blank=True)
	properties   = models.ManyToManyField('Property',    null=True, blank=True)
	signals      = models.ManyToManyField('Signal',      null=True, blank=True)
	parent_class = models.ForeignKey     ('self',        null=True, blank=True)
	interfaces   = models.ManyToManyField('Interface',   null=True, blank=True, related_name='class_interfaces')
	is_abstract  = models.BooleanField(default=False)

class Interface(Class):
	pass
