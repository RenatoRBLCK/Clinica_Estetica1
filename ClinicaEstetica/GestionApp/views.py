from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from .models import Producto, Cliente, Atencion, Colaborador, Proveedor, DetalleAtencionProducto
from .forms import (
    CustomUserCreationForm, ProductoForm, ClienteForm, AtencionForm, 
    DetalleAtencionFormSet, ColaboradorForm, ProveedorForm
)

# --- FUNCIONES DE AYUDA PARA PERMISOS ---

def es_recepcionista(user):
    # Verifica si es Admin O si tiene el cargo de RECEPCIONISTA en su ficha de Colaborador
    if user.is_staff: return True
    if hasattr(user, 'colaborador') and user.colaborador.cargo == 'RECEPCIONISTA':
        return True
    return False

def es_estilista(user):
    if user.is_staff: return True
    if hasattr(user, 'colaborador') and user.colaborador.cargo == 'ESTILISTA':
        return True
    return False

# -----------------------------------------------------------------------------
# VISTAS PÚBLICAS Y AUTENTICACIÓN
# -----------------------------------------------------------------------------

def home(request):
    return render(request, 'home.html')

def registro_usuario(request):
    from django.contrib.auth.models import User
    from django import forms

    class RegistroColaboradorForm(CustomUserCreationForm):
        CARGOS = [
            ('ESTILISTA', 'Estilista'),
            ('RECEPCIONISTA', 'Recepcionista'),
        ]
        cargo = forms.ChoiceField(choices=CARGOS, label="Cargo")

    if request.method == 'POST':
        form = RegistroColaboradorForm(request.POST)
        if form.is_valid():
            user = form.save()
            cargo = form.cleaned_data['cargo']
            # Crear el colaborador asociado
            Colaborador.objects.create(
                rut="TEMP", # Puedes pedir el rut en el formulario si lo necesitas
                nombre=user.username,
                telefono="",
                cargo=cargo,
                sueldo=0,
                usuario=user
            )
            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroColaboradorForm()
    return render(request, 'registration/registro.html', {'form': form})

def exit_sesion(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('home')

# -----------------------------------------------------------------------------
# PANEL DE GESTIÓN (Admin y Recepcionista)
# -----------------------------------------------------------------------------

@login_required
def panel_gestion(request):
    # Permite entrar a Admin y Recepcionista
    if not es_recepcionista(request.user):
        messages.error(request, 'Acceso denegado. No tienes permisos de gestión.')
        return redirect('home')
    return render(request, 'gestion/panel_gestion.html')

# -----------------------------------------------------------------------------
# CRUD PRODUCTOS (Solo Admin)
# -----------------------------------------------------------------------------

@login_required
def listar_productos(request):
    if not request.user.is_staff: return redirect('home')
    # CORRECCIÓN: Filtramos solo los productos activos (Baja Lógica)
    productos = Producto.objects.filter(activo=True)
    return render(request, 'gestion/productos/lista.html', {'productos': productos})

@login_required
def crear_producto(request):
    if not request.user.is_staff: return redirect('home')
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            # Validación: stock_actual y stock_minimo deben ser > 0
            if producto.stock_actual <= 0 or producto.stock_minimo <= 0:
                messages.error(request, 'El stock actual y el stock mínimo deben ser mayores a cero.')
                return render(request, 'gestion/productos/form.html', {'form': form, 'titulo': 'Crear Producto'})
            producto.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('listar_productos')
    else:
        form = ProductoForm()
    return render(request, 'gestion/productos/form.html', {'form': form, 'titulo': 'Crear Producto'})

@login_required
def editar_producto(request, id):
    if not request.user.is_staff: return redirect('home')
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto_editado = form.save(commit=False)
            # Validación: stock_actual y stock_minimo deben ser > 0
            if producto_editado.stock_actual <= 0 or producto_editado.stock_minimo <= 0:
                messages.error(request, 'El stock actual y el stock mínimo deben ser mayores a cero.')
                return render(request, 'gestion/productos/form.html', {'form': form, 'titulo': 'Editar Producto'})
            producto_editado.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('listar_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'gestion/productos/form.html', {'form': form, 'titulo': 'Editar Producto'})

@login_required
def eliminar_producto(request, id):
    if not request.user.is_staff: return redirect('home')
    producto = get_object_or_404(Producto, id=id)
    
    # CORRECCIÓN IMPORTANTE: Baja Lógica para evitar ProtectedError
    # En lugar de borrarlo físicamente, lo marcamos como inactivo.
    producto.activo = False
    producto.save()
    
    messages.success(request, 'Producto dado de baja exitosamente.')
    return redirect('listar_productos')

# -----------------------------------------------------------------------------
# CRUD CLIENTES (Admin y Recepcionista)
# -----------------------------------------------------------------------------

@login_required
def listar_clientes(request):
    if not es_recepcionista(request.user): return redirect('home')
    clientes = Cliente.objects.all()
    return render(request, 'gestion/clientes/lista.html', {'clientes': clientes})

@login_required
def crear_cliente(request):
    if not es_recepcionista(request.user): return redirect('home')
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente registrado exitosamente.')
            return redirect('listar_clientes')
    else:
        form = ClienteForm()
    return render(request, 'gestion/clientes/form.html', {'form': form, 'titulo': 'Registrar Cliente'})

@login_required
def editar_cliente(request, id):
    if not es_recepcionista(request.user): return redirect('home')
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos del cliente actualizados.')
            return redirect('listar_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'gestion/clientes/form.html', {'form': form, 'titulo': 'Editar Cliente'})

@login_required
def eliminar_cliente(request, id):
    if not es_recepcionista(request.user): return redirect('home')
    cliente = get_object_or_404(Cliente, id=id)
    cliente.activo = False
    cliente.save()
    messages.warning(request, 'Cliente dado de baja (Inactivo).')
    return redirect('listar_clientes')

# -----------------------------------------------------------------------------
# CRUD COLABORADORES (Solo Admin)
# -----------------------------------------------------------------------------

@login_required
def listar_colaboradores(request):
    if not request.user.is_staff: return redirect('home')
    colaboradores = Colaborador.objects.all()
    return render(request, 'gestion/colaboradores/lista.html', {'colaboradores': colaboradores})

@login_required
def crear_colaborador(request):
    if not request.user.is_staff: return redirect('home')
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Colaborador registrado exitosamente.')
            return redirect('listar_colaboradores')
    else:
        form = ColaboradorForm()
    return render(request, 'gestion/colaboradores/form.html', {'form': form, 'titulo': 'Registrar Colaborador'})

@login_required
def editar_colaborador(request, id):
    if not request.user.is_staff: return redirect('home')
    colaborador = get_object_or_404(Colaborador, id=id)
    if request.method == 'POST':
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()
            messages.success(request, 'Información del colaborador actualizada.')
            return redirect('listar_colaboradores')
    else:
        form = ColaboradorForm(instance=colaborador)
    return render(request, 'gestion/colaboradores/form.html', {'form': form, 'titulo': 'Editar Colaborador'})

@login_required
def eliminar_colaborador(request, id):
    if not request.user.is_staff: return redirect('home')
    colaborador = get_object_or_404(Colaborador, id=id)
    colaborador.delete()
    messages.success(request, 'Colaborador eliminado permanentemente.')
    return redirect('listar_colaboradores')

# -----------------------------------------------------------------------------
# CRUD PROVEEDORES (Solo Admin)
# -----------------------------------------------------------------------------

@login_required
def listar_proveedores(request):
    if not request.user.is_staff: return redirect('home')
    proveedores = Proveedor.objects.all()
    return render(request, 'gestion/proveedores/lista.html', {'proveedores': proveedores})

@login_required
def crear_proveedor(request):
    if not request.user.is_staff: return redirect('home')
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor registrado exitosamente.')
            return redirect('listar_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'gestion/proveedores/form.html', {'form': form, 'titulo': 'Registrar Proveedor'})

@login_required
def editar_proveedor(request, id):
    if not request.user.is_staff: return redirect('home')
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Información del proveedor actualizada.')
            return redirect('listar_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'gestion/proveedores/form.html', {'form': form, 'titulo': 'Editar Proveedor'})

@login_required
def eliminar_proveedor(request, id):
    if not request.user.is_staff: return redirect('home')
    proveedor = get_object_or_404(Proveedor, id=id)
    proveedor.delete()
    messages.success(request, 'Proveedor eliminado permanentemente.')
    return redirect('listar_proveedores')

# -----------------------------------------------------------------------------
# REPORTES (Admin)
# -----------------------------------------------------------------------------

@login_required
def reporte_stock_critico(request):
    productos_criticos = []
    # Filtramos solo los productos activos para el reporte
    todos_productos = Producto.objects.filter(activo=True)
    
    for p in todos_productos:
        if p.esta_bajo_stock():
            productos_criticos.append(p)
            
    return render(request, 'gestion/productos/lista_criticos.html', {'productos': productos_criticos})

# -----------------------------------------------------------------------------
# PROCESO DE NEGOCIO: REGISTRAR ATENCIÓN (Estilista)
# -----------------------------------------------------------------------------

@login_required
def registrar_atencion(request):
    if not es_estilista(request.user):
        messages.error(request, 'Acceso denegado. Solo estilistas pueden registrar atenciones.')
        return redirect('home')
    if request.method == 'POST':
        form_atencion = AtencionForm(request.POST)
        productos_ids = request.POST.getlist('producto[]')
        cantidades = request.POST.getlist('cantidad[]')
        
        if form_atencion.is_valid():
            atencion = form_atencion.save(commit=False)
            atencion.estilista = request.user
            cliente = form_atencion.cleaned_data['cliente']
            hoy = timezone.now().date()
            if cliente.fecha_nacimiento.month == hoy.month and cliente.fecha_nacimiento.day == hoy.day:
                atencion.descuento_aplicado = True
                messages.info(request, f"¡Feliz Cumpleaños a {cliente.nombre}! Se aplicó un 20% de descuento.")
            atencion.save()
            servicios_seleccionados = form_atencion.cleaned_data['servicios']
            atencion.servicios.set(servicios_seleccionados)
            total_servicios = sum([s.precio_mano_obra for s in servicios_seleccionados])
            total_productos = 0
            for prod_id, cant in zip(productos_ids, cantidades):
                if prod_id and cant:
                    producto = Producto.objects.get(id=prod_id)
                    cantidad = int(cant)
                    if producto.stock_actual >= cantidad:
                        producto.stock_actual -= cantidad
                        producto.save()
                        DetalleAtencionProducto.objects.create(
                            atencion=atencion,
                            producto=producto,
                            cantidad=cantidad
                        )
                        total_productos += (producto.precio * cantidad)
                        # NUEVO: Avisar si el producto queda bajo mínimos después de la compra
                        if producto.esta_bajo_stock():
                            messages.warning(
                                request,
                                f"Advertencia: El producto '{producto.nombre}' ha quedado bajo el stock mínimo después de esta compra."
                            )
                    else:
                        messages.error(request, f"ERROR: No hay suficiente stock de {producto.nombre}.")
                        atencion.delete()
                        return redirect('registrar_atencion')
            subtotal = total_servicios + total_productos
            if atencion.descuento_aplicado:
                total_final = int(subtotal * 0.8)
            else:
                total_final = subtotal
            atencion.total_pagar = total_final
            atencion.save()
            messages.success(request, f"Atención registrada con éxito. Total a pagar: ${total_final}")
            return redirect('home')
    else:
        form_atencion = AtencionForm()
        productos = Producto.objects.filter(activo=True)
    return render(request, 'operacion/registrar_atencion.html', {
        'form_atencion': form_atencion,
        'productos': Producto.objects.filter(activo=True)
    })

@login_required
def productos_estilista(request):
    if not es_estilista(request.user):
        messages.error(request, 'Acceso denegado. Solo estilistas pueden consultar productos.')
        return redirect('home')
    productos = Producto.objects.filter(activo=True)
    return render(request, 'gestion/productos/lista_estilista.html', {'productos': productos})

@login_required
def productos_criticos_estilista(request):
    if not es_estilista(request.user):
        messages.error(request, 'Acceso denegado. Solo estilistas pueden consultar productos críticos.')
        return redirect('home')
    productos_criticos = [p for p in Producto.objects.filter(activo=True) if p.esta_bajo_stock()]
    return render(request, 'gestion/productos/lista_criticos_estilista.html', {'productos': productos_criticos})