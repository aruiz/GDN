from django.db import models

class Symbol(models.Model):
  name = models.CharField()
  namespace = models.CharField()
  doc = models.TextField (null=True)

class Class(Symbol):
  parent = Classes(null=True)
  implements = models.ManyToManyField(Interface)
  methods = models.ManyToManyField()

class Delegate(Symbol):

class Method(Symbol):
  is_virtual = models.BooleanField()
  is_static = models.BooleanField()

class Interface(Symbol):
  parent = Interface(null=True)

class Enum(Symbol):
  pass

class EnumValue(Symbol):
  enum_type = models ForeignKey(Enum)
  value = models.IntegerField()
  
class Bitfield(Symbol):
  pass

class BitfieldValue(Symbol):
  bitfield = models.ForeignKey(Bitfield)
  value = models.IntegerField()

class BuiltIn(Symbol):
  c_type = models.CharField()
  
class Constant(Symbol):
  type_symbol = models.ForeignKey(Symbol)
  c_type = models.CharField()
  value = models.CharField()

# Create your models here.
