# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from django.db import models

class Symbol(models.Model):
  name = models.CharField(max_length=500)
  namespace = models.CharField(max_length=500)
  doc = models.TextField (null=True)

class Class(Symbol):
  parent = models.ForeignKey('self', null=True)
  implements = models.ManyToManyField('Interface')
  methods = models.ManyToManyField('Method', null=True)

class Delegate(Symbol):
  pass

class Method(Symbol):
  is_virtual = models.BooleanField()
  is_static = models.BooleanField()

class Interface(Symbol):
  parent = models.ForeignKey('self', null=True)

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

class BuiltIn(Symbol):
  c_type = models.CharField(max_length=500)
  
class Constant(Symbol):
  type_symbol = models.ForeignKey(Symbol, related_name="tpye_symbol")
  c_type = models.CharField(max_length=500)
  value = models.CharField(max_length=500)

# Create your models here.
