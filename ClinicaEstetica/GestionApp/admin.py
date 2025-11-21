from django.contrib import admin
from .models import Producto, Cliente, Servicio, Atencion, DetalleAtencionProducto


# Configuración de PRODUCTO
class ProductoAdmin(admin.ModelAdmin):
    # Mostramos columnas útiles, incluyendo el método personalizado 'esta_bajo_stock'
    list_display = ('nombre', 'precio', 'stock_actual', 'stock_minimo', 'ver_estado_stock')
    search_fields = ('nombre',)
    list_filter = ('stock_actual',)

    # Personalizamos cómo se ve el método en el admin
    def ver_estado_stock(self, obj):
        return obj.esta_bajo_stock()
    ver_estado_stock.boolean = True # Pone un icono de check/cruz
    ver_estado_stock.short_description = '¿Bajo Stock Crítico?'

# Configuración de CLIENTE
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'telefono', 'fecha_nacimiento', 'activo')
    search_fields = ('rut', 'nombre')
    list_filter = ('activo',)

# Configuración de SERVICIO
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_mano_obra')

# Configuración de ATENCIÓN (Visitas)

class AtencionAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'estilista', 'servicio', 'fecha', 'total_pagar', 'descuento_aplicado')
    list_filter = ('fecha', 'estilista', 'descuento_aplicado')
    search_fields = ('cliente__nombre', 'cliente__rut')

# Configuración de DETALLE (Productos usados)
class DetalleAtencionProductoAdmin(admin.ModelAdmin):
    list_display = ('atencion', 'producto', 'cantidad')

# Registro final de modelos en el sitio
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(Atencion, AtencionAdmin)
admin.site.register(DetalleAtencionProducto, DetalleAtencionProductoAdmin)