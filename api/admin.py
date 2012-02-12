# vim: tabstop=4 noexpandtab shiftwidth=4 softtabstop=4
from api.models import *
from django.contrib import admin

class SymbolAdmin(admin.ModelAdmin):
  list_display = ('name', 'namespaced_name', 'namespace')

class NsAdmin(admin.ModelAdmin):
  list_display = ('name',)

class TypeAdmin(admin.ModelAdmin):
  list_display = ('c_type',)

admin.site.register(Node,       SymbolAdmin)
admin.site.register(Namespace,  NsAdmin)
admin.site.register(Method,     SymbolAdmin)
admin.site.register(Callback,   TypeAdmin)
admin.site.register(Callable,   SymbolAdmin)
admin.site.register(Function,   SymbolAdmin)
admin.site.register(Type,       SymbolAdmin)
admin.site.register(Record,     SymbolAdmin)

admin.site.register(Value,       SymbolAdmin)
admin.site.register(Enumeration, SymbolAdmin)

admin.site.register(TypedNode,  NsAdmin)
admin.site.register(Parameter,  NsAdmin)
admin.site.register(ReturnValue,  NsAdmin)
admin.site.register(Field,       NsAdmin)

admin.site.register(Class,    SymbolAdmin)
admin.site.register(Interface, SymbolAdmin)
