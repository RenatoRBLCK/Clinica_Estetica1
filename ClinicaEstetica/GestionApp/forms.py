from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from .models import Producto, Cliente, Atencion, DetalleAtencionProducto, Colaborador, Proveedor, Servicio

# Formulario de Registro de Usuario 
class CustomUserCreationForm(UserCreationForm):
    pass

# Formulario de Producto 
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# Formulario de Cliente 
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# Formulario para LA ATENCIÓN
class AtencionForm(forms.ModelForm):
    servicios = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        label="Servicios Realizados"
    )

    class Meta:
        model = Atencion
        fields = ['cliente', 'servicios']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(activo=True)
        self.fields['servicios'].queryset = Servicio.objects.all()

    def clean_cliente(self):
        cliente = self.cleaned_data.get('cliente')
        if cliente and not cliente.activo:
            raise forms.ValidationError("El cliente está dado de baja y no puede recibir una atención.")
        return cliente

# Formulario para DETALLES 
class DetalleAtencionForm(forms.ModelForm):
    class Meta:
        model = DetalleAtencionProducto
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo productos activos en el desplegable
        self.fields['producto'].queryset = Producto.objects.filter(activo=True)

    def clean_producto(self):
        producto = self.cleaned_data.get('producto')
        if producto and not producto.activo:
            raise forms.ValidationError("El producto no existe actualmente.")
        return producto

DetalleAtencionFormSet = inlineformset_factory(
    Atencion, 
    DetalleAtencionProducto, 
    form=DetalleAtencionForm,
    extra=3, 
    can_delete=True
)


# Formulario para COLABORADORES 
# Gestionar estilistas y recepcionistas

class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = '__all__'
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.Select(attrs={'class': 'form-select'}),
            'sueldo': forms.NumberInput(attrs={'class': 'form-control'}),
            'usuario': forms.Select(attrs={'class': 'form-select'}),
        }


# Formulario para PROVEEDORES 
# Gestionar contactos de proveedores

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'productos_suministrados': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }