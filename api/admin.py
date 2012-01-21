from api.models import *
from django.contrib import admin

class SymbolAdmin(admin.ModelAdmin):
  list_display = ('c_type', 'name', 'namespaced_name', 'namespace')

admin.site.register(Delegate, SymbolAdmin)
admin.site.register(Method, SymbolAdmin)
admin.site.register(Interface, SymbolAdmin)
admin.site.register(Enum)
admin.site.register(EnumValue)
admin.site.register(Bitfield, SymbolAdmin)
admin.site.register(BitfieldValue)
admin.site.register(BuiltIn)
admin.site.register(Constant)

admin.site.register(Symbol, SymbolAdmin)
admin.site.register(Class,  SymbolAdmin)
