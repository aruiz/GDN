# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from api.models import *
from django.contrib import admin

class NsAdmin(admin.ModelAdmin):
  list_display = ('name','version')
admin.site.register(Namespace,  NsAdmin)

class NodeAdmin(admin.ModelAdmin):
	list_display = ('gi_name', 'c_name', 'namespace', 'foreign')
admin.site.register(Node,  NodeAdmin)
admin.site.register(Record,  NodeAdmin)

class EnumAdmin(admin.ModelAdmin):
	list_display = ('name', 'ctype')
admin.site.register(Enum,  EnumAdmin)

class BitfieldAdmin(admin.ModelAdmin):
	list_display = ('name', 'ctype')
admin.site.register(Bitfield,  BitfieldAdmin)

class MemberAdmin(admin.ModelAdmin):
	list_display = ('name', 'value')
admin.site.register(Member,  MemberAdmin)

class AliasAdmin(admin.ModelAdmin):
	list_display = ('name',)
admin.site.register(Alias, AliasAdmin)

class TypeAdmin(admin.ModelAdmin):
	list_display = ('ctype',)
admin.site.register(Type, TypeAdmin)
admin.site.register(TypeUnknown, TypeAdmin)
admin.site.register(Varargs, TypeAdmin)
admin.site.register(Array, TypeAdmin)
admin.site.register(List, TypeAdmin)
admin.site.register(Map, TypeAdmin)

class TypeContainerAdmin(admin.ModelAdmin):
	list_display = ('type', 'transfer')
admin.site.register(TypeContainer, TypeContainerAdmin)
admin.site.register(Return, TypeContainerAdmin)
admin.site.register(Parameter, TypeContainerAdmin)

class FunctionAdmin(admin.ModelAdmin):
	list_display = ('c_name', 'gi_name', 'instance_parameter')
admin.site.register(Function, FunctionAdmin)

class FunctionParameterAdmin(admin.ModelAdmin):
	list_display = ('function', 'parameter', 'position')
admin.site.register(FunctionParameter, FunctionParameterAdmin)

"""
class SymbolAdmin(admin.ModelAdmin):
  list_display = ('name', 'namespaced_name', 'namespace')

class TypeAdmin(admin.ModelAdmin):
  list_display = ('name', 'namespaced_name', 'c_type',)

class EnumAdmin(admin.ModelAdmin):
  list_display = ('name', 'namespaced_name', 'c_type', 'is_bitfield')

admin.site.register(Node,       SymbolAdmin)
admin.site.register(Method,     SymbolAdmin)
admin.site.register(Callback,   TypeAdmin)
admin.site.register(Callable,   SymbolAdmin)
admin.site.register(Function,   SymbolAdmin)
admin.site.register(Type,       TypeAdmin)
admin.site.register(Record,     SymbolAdmin)

admin.site.register(Value,       SymbolAdmin)
admin.site.register(Enumeration, TypeAdmin)

admin.site.register(TypedNode,  NsAdmin)
admin.site.register(Parameter,  NsAdmin)
admin.site.register(ReturnValue,  NsAdmin)
admin.site.register(Field,       NsAdmin)

admin.site.register(Class,    SymbolAdmin)
admin.site.register(Interface, SymbolAdmin)
"""
