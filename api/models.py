# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.db import models

class Type(models.Model):
  name   = models.CharField(max_length=500)

class Symbol(Type):
  c_type = models.CharField(max_length=500, unique=True)
  namespaced_name = models.CharField(max_length=500, unique=True)
  namespace = models.CharField(max_length=500)
  doc = models.TextField (null=True, blank=True)

class Class(Symbol):
  parent = models.ForeignKey('self', null=True, blank=True)
  implements = models.ManyToManyField('Interface', null=True, blank=True)
  methods = models.ManyToManyField('Method', null=True, blank=True)

class Callable(Symbol):
  pass

class Method(Symbol):
  is_virtual = models.BooleanField(default=False)
  is_static = models.BooleanField(default=False)

class Interface(Symbol):
  parent = models.ForeignKey('self', null=True, blank=True)

class Enum(Symbol):
  pass

class EnumValue(Symbol):
  enum_type = models.ForeignKey(Enum)
  value = models.IntegerField()
  
class Bitfield(Symbol):
  pass

class BitfieldValue(Symbol):
  bitfield = models.ForeignKey(Bitfield)
  value = models.IntegerField()

class BuiltIn(Type):
  c_type = models.CharField(max_length=500)
  pass

class Constant(Symbol):
  type_symbol = models.ForeignKey(Symbol, related_name="type_symbol")
  value = models.CharField(max_length=500)
