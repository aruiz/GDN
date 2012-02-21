# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from api.models import *
from django.contrib import admin

class NsAdmin(admin.ModelAdmin):
  list_display = ('name','version')
admin.site.register(Namespace,  NsAdmin)


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
