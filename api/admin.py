# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from api.models import *
from django.contrib import admin

class NsAdmin(admin.ModelAdmin):
  list_display = ('name','version')
admin.site.register(Namespace,  NsAdmin)

class NodeAdmin(admin.ModelAdmin):
	list_display = ('gi_name', 'c_name', 'namespace', 'foreign')
	list_filter = ('namespace', )
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
	list_filter = ('namespace', 'cls_methods')
admin.site.register(Function, FunctionAdmin)

class FunctionParameterAdmin(admin.ModelAdmin):
	list_display = ('function', 'parameter', 'position')
admin.site.register(FunctionParameter, FunctionParameterAdmin)

class ClassAdmin(admin.ModelAdmin):
	list_display = ('c_name', 'gi_name')
	list_filter = ('namespace', )
admin.site.register(Class, ClassAdmin)
