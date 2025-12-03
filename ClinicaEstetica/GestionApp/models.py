from django.db import models
from django.contrib.auth.models import User

# MODELO PRODUCTO (Inventario)
class Producto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre Producto")
    descripcion = models.TextField(verbose_name="Descripción", blank=True)
    precio = models.IntegerField(verbose_name="Precio Unitario")
    stock_actual = models.IntegerField(verbose_name="Stock Actual")
    stock_minimo = models.IntegerField(verbose_name="Stock Mínimo Crítico")
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    activo = models.BooleanField(default=True, verbose_name="Producto Activo")

    def __str__(self):
        return f"{self.nombre} (Stock: {self.stock_actual})"
    
    def esta_bajo_stock(self):
        return self.stock_actual <= self.stock_minimo

# MODELO CLIENTE
class Cliente(models.Model):
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email", null=True, blank=True)
    
    #  Vital para calcular el descuento de cumpleaños
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    
    #  Para dar de baja lógica (inactivos) sin borrar el historial
    activo = models.BooleanField(default=True, verbose_name="Cliente Activo")

    def __str__(self):
        return f"{self.nombre} ({self.rut})"

#  MODELO SERVICIO (Catálogo de Servicios)
class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    precio_mano_obra = models.IntegerField(verbose_name="Precio Base Servicio")

    def __str__(self):
        return f"{self.nombre} - ${self.precio_mano_obra}"

#  MODELO ATENCION (Registro de Visita)
class Atencion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    
    #  El estilista es un usuario del sistema (Colaborador)
    estilista = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Estilista a cargo")
    
    # Cambia a ManyToManyField para servicios
    servicios = models.ManyToManyField(Servicio, verbose_name="Servicios Realizados")
    fecha = models.DateTimeField(auto_now_add=True)
    
    # Productos consumidos en esta atención (Relación Muchos a Muchos)
    # Un servicio puede usar varios productos
    productos = models.ManyToManyField(Producto, through='DetalleAtencionProducto')
    
    # Totales calculados
    total_pagar = models.IntegerField(default=0)
    
    #  Para registrar si se aplicó el descuento
    descuento_aplicado = models.BooleanField(default=False, verbose_name="Descuento Cumpleaños Aplicado")

    def __str__(self):
        return f"Atención #{self.id} - {self.cliente.nombre}"

# Tabla intermedia para saber CUÁNTO de cada producto se usó
class DetalleAtencionProducto(models.Model):
    atencion = models.ForeignKey(Atencion, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1, verbose_name="Cantidad Usada")

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en Atención #{self.atencion.id}"
    
class Colaborador(models.Model):
    CARGOS = [
        ('ESTILISTA', 'Estilista'),
        ('RECEPCIONISTA', 'Recepcionista'),
        ('ADMINISTRADOR', 'Administrador'),
    ]
    
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono")
    cargo = models.CharField(max_length=20, choices=CARGOS, verbose_name="Cargo")
    sueldo = models.IntegerField(verbose_name="Sueldo Base")
    
    # Vincular con el usuario de Django para que pueda loguearse
    usuario = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario de Sistema")

    def __str__(self):
        return f"{self.nombre} ({self.get_cargo_display()})"

#  MODELO PROVEEDOR (HU19)
class Proveedor(models.Model):
    nombre_empresa = models.CharField(max_length=100, verbose_name="Empresa")
    contacto_nombre = models.CharField(max_length=100, verbose_name="Nombre Contacto")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email", blank=True)
    direccion = models.CharField(max_length=200, verbose_name="Dirección", blank=True)
    
    # Descripción de qué productos nos vende 
    productos_suministrados = models.TextField(verbose_name="Productos que suministra")

    def __str__(self):
        return self.nombre_empresa