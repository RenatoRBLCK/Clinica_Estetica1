from django.urls import path
from . import views

urlpatterns = [
    # Vistas Públicas y Auth 
    path('', views.home, name='home'),
    path('registro/', views.registro_usuario, name='registro'),
    path('logout/', views.exit_sesion, name='exit'),

    # Panel de Gestión
    path('gestion/', views.panel_gestion, name='panel_gestion'),

    # CRUD PRODUCTOS
    path('gestion/productos/', views.listar_productos, name='listar_productos'),
    path('gestion/productos/crear/', views.crear_producto, name='crear_producto'),
    path('gestion/productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('gestion/productos/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    
    # Reporte de Stock Crítico
    path('gestion/productos/criticos/', views.reporte_stock_critico, name='reporte_stock_critico'),

    # CRUD CLIENTES
    path('gestion/clientes/', views.listar_clientes, name='listar_clientes'),
    path('gestion/clientes/crear/', views.crear_cliente, name='crear_cliente'),
    path('gestion/clientes/editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('gestion/clientes/eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),

    # CRUD COLABORADORES 
    path('gestion/colaboradores/', views.listar_colaboradores, name='listar_colaboradores'),
    path('gestion/colaboradores/crear/', views.crear_colaborador, name='crear_colaborador'),
    path('gestion/colaboradores/editar/<int:id>/', views.editar_colaborador, name='editar_colaborador'),
    path('gestion/colaboradores/eliminar/<int:id>/', views.eliminar_colaborador, name='eliminar_colaborador'),

    # CRUD PROVEEDORES 
    path('gestion/proveedores/', views.listar_proveedores, name='listar_proveedores'),
    path('gestion/proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('gestion/proveedores/editar/<int:id>/', views.editar_proveedor, name='editar_proveedor'),
    path('gestion/proveedores/eliminar/<int:id>/', views.eliminar_proveedor, name='eliminar_proveedor'),

    # PROCESO DE NEGOCIO 
    path('atencion/registrar/', views.registrar_atencion, name='registrar_atencion'),

    # Consulta de productos para estilista
    path('productos/estilista/', views.productos_estilista, name='productos_estilista'),
    path('productos/criticos/estilista/', views.productos_criticos_estilista, name='productos_criticos_estilista'),
]