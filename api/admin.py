from api.models import *
from django.contrib import admin

class SymbolAdmin(admin.ModelAdmin):
  list_display = ('name', 'namespaced_name', 'namespace')

class NsAdmin(admin.ModelAdmin):
  list_display = ('name',)

admin.site.register(Node,       SymbolAdmin)
admin.site.register(Namespace,  NsAdmin)

#admin.site.register(Callable, SymbolAdmin)
#admin.site.register(Method, SymbolAdmin)
#admin.site.register(Interface, SymbolAdmin)

#admin.site.register(Enum)
#admin.site.register(EnumValue)
#admin.site.register(Bitfield, SymbolAdmin)
#admin.site.register(BitfieldValue)
#admin.site.register(Symbol, SymbolAdmin)
