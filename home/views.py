from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from .models import (
    Escaparate, Articulo, Cliente, 
    Producto, Categoria, Marca, Carrito, ItemCarrito, Pedido, ItemPedido, ConfiguracionEnvio
)
from decimal import Decimal
import uuid
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import braintree

# Configurar Braintree
gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=settings.BRAINTREE_MERCHANT_ID,
        public_key=settings.BRAINTREE_PUBLIC_KEY,
        private_key=settings.BRAINTREE_PRIVATE_KEY
    )
)

# Email especial para la cuenta de invitado del sistema
EMAIL_INVITADO_SISTEMA = 'invitado@sistema.local'


def calcular_coste_envio(subtotal):
    """Calcular el coste de envío según la configuración del sistema"""
    config = ConfiguracionEnvio.get_configuracion()
    if subtotal >= config.envio_minimo_gratis:
        return Decimal('0.00')
    return config.coste_envio_estandar


def determinar_estado_pedido(metodo_pago):
    """Determinar el estado inicial del pedido según el método de pago"""
    if metodo_pago == 'reembolso':
        return 'en_espera_pago'
    return 'confirmado'

def obtener_invitado_sistema():
    """Obtiene o crea la cuenta de invitado única del sistema"""
    invitado, created = Cliente.objects.get_or_create(
        email=EMAIL_INVITADO_SISTEMA,
        defaults={
            'nombre': 'Invitado',
            'apellidos': 'Sistema',
            'telefono': '000000000',
            'direccion': 'N/A',
            'ciudad': 'N/A',
            'codigo_postal': '00000',
            'password': ''
        }
    )
    return invitado

def es_usuario_admin(request):
    """Helper para verificar si el usuario actual es administrador"""
    cliente_id = request.session.get('cliente_id')
    if cliente_id:
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            return cliente.is_admin
        except Cliente.DoesNotExist:
            pass
    return False

def bloquear_acceso_admin(request):
    """Redirigir a admin panel si el usuario es administrador"""
    if es_usuario_admin(request):
        return redirect('admin_panel')
    return None

def obtener_cantidad_carrito(request):
    """Helper para obtener la cantidad de items en el carrito"""
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return 0
    
    try:
        carrito = Carrito.objects.get(cliente_id=cliente_id)
        return carrito.items.count()
    except Carrito.DoesNotExist:
        return 0

def obtener_info_carrito(request):
    """Helper para obtener información completa del carrito para el mini-carrito"""
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return {
            'items': [],
            'cantidad_total': 0,
            'subtotal': Decimal('0.00'),
            'tiene_items': False
        }
    
    try:
        carrito = Carrito.objects.get(cliente_id=cliente_id)
        items = carrito.items.all()  # Todos los items para mostrar en el mini-carrito con scroll
        
        items_con_total = []
        subtotal = Decimal('0.00')
        
        for item in items:
            precio = item.producto.precio
            total_item = (precio * item.cantidad).quantize(Decimal('0.01'))
            subtotal += total_item
            items_con_total.append({
                'item': item,
                'precio_unitario': precio,
                'total': total_item
            })
        
        return {
            'items': items_con_total,
            'cantidad_total': carrito.items.count(),
            'subtotal': subtotal.quantize(Decimal('0.01')),
            'tiene_items': carrito.items.exists()
        }
    except Carrito.DoesNotExist:
        return {
            'items': [],
            'cantidad_total': 0,
            'subtotal': Decimal('0.00'),
            'tiene_items': False
        }

def index(request):
    escaparate = Escaparate.objects.first()
    
    if not escaparate or not escaparate.articulo:
        return HttpResponse("No hay escaparates o artículos disponibles.")
    
    articulo = escaparate.articulo
    
    contexto = {
        'nombre_articulo': articulo.nombre
    }
    
    plantilla = loader.get_template('index.html')
    return HttpResponse(plantilla.render(contexto, request))

def mainPage(request):
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    # Obtener productos destacados
    productos_destacados = Producto.objects.filter(
        es_destacado=True
    ).distinct()[:4]  # Mostrar máximo 4 productos
    
    contexto = {
        'productos_destacados': productos_destacados,
        'cart_info': obtener_info_carrito(request),
        'user_is_admin': es_usuario_admin(request)
    }
    
    mainPage = loader.get_template('mainPage.html')
    return HttpResponse(mainPage.render(contexto, request))

def terminos(request):
    """Vista para términos y condiciones"""
    contexto = {
        'cart_info': obtener_info_carrito(request)
    }
    return render(request, 'terminos.html', contexto)
    return HttpResponse(mainPage.render(contexto, request))

def user(request):
    """Redirige a login o perfil dependiendo de si está autenticado"""
    cliente_id = request.session.get('cliente_id')
    
    if cliente_id:
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            # Si es invitado, redirigir a login para que se registre
            es_invitado = request.session.get('es_invitado', False) or cliente.email == EMAIL_INVITADO_SISTEMA
            if es_invitado:
                return redirect('login')
            # Si es admin, ir a panel admin
            if es_usuario_admin(request):
                return redirect('admin_perfil')
            else:
                return redirect('perfil')
        except Cliente.DoesNotExist:
            request.session.flush()
            return redirect('login')
    else:
        # Si no está autenticado, ir al login
        return redirect('login')

def login(request):
    """Vista de login"""
    # Si ya está autenticado como usuario real (no invitado), redirigir al perfil
    cliente_id = request.session.get('cliente_id')
    if cliente_id:
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            es_invitado = request.session.get('es_invitado', False) or cliente.email == EMAIL_INVITADO_SISTEMA
            if not es_invitado:
                return redirect('perfil')
        except Cliente.DoesNotExist:
            pass
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # Buscar cliente por email
            cliente = Cliente.objects.get(email=email)
            
            # Verificar contraseña
            if cliente.password == password:
                # Guardar el ID del cliente en la sesión
                request.session['cliente_id'] = cliente.id
                # Limpiar flag de invitado si existía
                if 'es_invitado' in request.session:
                    del request.session['es_invitado']
                # Redirigir según tipo de usuario
                if cliente.is_admin:
                    return redirect('admin_panel')
                else:
                    return redirect('perfil')
            else:
                contexto = {
                    'error': 'Email o contraseña incorrectos',
                    'email': email,
                }
                return render(request, 'login.html', contexto)
        except Cliente.DoesNotExist:
            contexto = {
                'error': 'Email o contraseña incorrectos',
                'email': email,
            }
            return render(request, 'login.html', contexto)
    
    return render(request, 'login.html')

def registro(request):
    """Vista de registro"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    # Si ya está autenticado como usuario real (no invitado), redirigir al perfil
    cliente_id = request.session.get('cliente_id')
    if cliente_id:
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            es_invitado = request.session.get('es_invitado', False) or cliente.email == EMAIL_INVITADO_SISTEMA
            if not es_invitado:
                return redirect('perfil')
        except Cliente.DoesNotExist:
            pass
    
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        codigo_postal = request.POST.get('codigo_postal')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        metodo_pago_favorito = request.POST.get('metodo_pago_favorito', 'tarjeta')
        
        # Validaciones
        if password != password_confirm:
            contexto = {
                'error': 'Las contraseñas no coinciden',
                'nombre': nombre,
                'apellidos': apellidos,
                'email': email,
                'telefono': telefono,
                'direccion': direccion,
                'ciudad': ciudad,
                'codigo_postal': codigo_postal,
            }
            return render(request, 'registro.html', contexto)
        
        # Verificar si el email ya existe
        if Cliente.objects.filter(email=email).exists():
            contexto = {
                'error': 'Este email ya está registrado',
                'nombre': nombre,
                'apellidos': apellidos,
                'telefono': telefono,
                'direccion': direccion,
                'ciudad': ciudad,
                'codigo_postal': codigo_postal,
            }
            return render(request, 'registro.html', contexto)
        
        # Crear el cliente
        try:
            cliente = Cliente.objects.create(
                nombre=nombre,
                apellidos=apellidos,
                email=email,
                telefono=telefono,
                direccion=direccion,
                ciudad=ciudad,
                codigo_postal=codigo_postal,
                password=password,
                metodo_pago_favorito=metodo_pago_favorito
            )
            
            # Autenticar automáticamente después del registro
            request.session['cliente_id'] = cliente.id
            # Limpiar flag de invitado si existía
            if 'es_invitado' in request.session:
                del request.session['es_invitado']
            return redirect('perfil')
            
        except Exception as e:
            contexto = {
                'error': f'Error al crear la cuenta: {str(e)}',
                'nombre': nombre,
                'apellidos': apellidos,
                'email': email,
                'telefono': telefono,
                'direccion': direccion,
                'ciudad': ciudad,
                'codigo_postal': codigo_postal,
            }
            return render(request, 'registro.html', contexto)
    
    # Si es GET, mostrar el formulario vacío
    return render(request, 'registro.html')

def perfil(request):
    """Vista del perfil de usuario"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        # Si el cliente no existe, cerrar sesión y redirigir al login
        request.session.flush()
        return redirect('login')
    
    # Verificar si es invitado (no puede editar perfil)
    es_invitado = request.session.get('es_invitado', False) or cliente.email == EMAIL_INVITADO_SISTEMA
    
    if es_invitado:
        # Los invitados no pueden editar perfil, redirigir con mensaje
        return redirect('mainPage')
    
    if request.method == 'POST':
        # Actualizar datos del cliente
        cliente.nombre = request.POST.get('nombre')
        cliente.apellidos = request.POST.get('apellidos')
        cliente.email = request.POST.get('email')
        cliente.telefono = request.POST.get('telefono')
        cliente.direccion = request.POST.get('direccion')
        cliente.ciudad = request.POST.get('ciudad')
        cliente.codigo_postal = request.POST.get('codigo_postal')
        cliente.metodo_pago_favorito = request.POST.get('metodo_pago_favorito', cliente.metodo_pago_favorito)
        
        # Cambiar contraseña si se proporcionó
        password_actual = request.POST.get('password_actual')
        password_nueva = request.POST.get('password_nueva')
        password_confirmar = request.POST.get('password_confirmar')
        
        if password_actual or password_nueva or password_confirmar:
            if password_actual != cliente.password:
                contexto = {
                    'cliente': cliente,
                    'error': 'La contraseña actual es incorrecta'
                }
                return render(request, 'perfil.html', contexto)
            
            if password_nueva != password_confirmar:
                contexto = {
                    'cliente': cliente,
                    'error': 'Las contraseñas nuevas no coinciden'
                }
                return render(request, 'perfil.html', contexto)
            
            if password_nueva:
                cliente.password = password_nueva
        
        try:
            cliente.save()
            contexto = {
                'cliente': cliente,
                'success': 'Perfil actualizado correctamente'
            }
            return render(request, 'perfil.html', contexto)
        except Exception as e:
            contexto = {
                'cliente': cliente,
                'error': f'Error al actualizar el perfil: {str(e)}'
            }
            return render(request, 'perfil.html', contexto)
    
    contexto = {
        'cliente': cliente,
    }
    return render(request, 'perfil.html', contexto)

def admin_perfil(request):
    """Vista del perfil de administrador - solo permite cerrar sesión"""
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        # Verificar que sea admin
        if not cliente.is_admin:
            return redirect('perfil')
    except Cliente.DoesNotExist:
        request.session.flush()
        return redirect('login')
    
    contexto = {
        'cliente': cliente,
        'user_is_admin': True,
        'cart_info': obtener_info_carrito(request)
    }
    return render(request, 'admin_perfil.html', contexto)

def logout(request):
    """Cerrar sesión"""
    request.session.flush()
    return redirect('mainPage')

def eliminar_cuenta(request):
    """Eliminar cuenta de usuario"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        cliente.delete()
        request.session.flush()
        return redirect('mainPage')
    except Cliente.DoesNotExist:
        request.session.flush()
        return redirect('login')

def productos(request):
    """Vista de listado de productos con filtros múltiples"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    from django.db.models import Q
    
    # Obtener todos los productos disponibles
    productos_list = Producto.objects.filter(esta_disponible=True)
    
    # Filtro por búsqueda (busca en nombre, descripción, marca y categoría)
    buscar = request.GET.get('buscar', '').strip()
    if buscar:
        productos_list = productos_list.filter(
            Q(nombre__icontains=buscar) |
            Q(descripcion__icontains=buscar) |
            Q(marca__nombre__icontains=buscar) |
            Q(categoria__nombre__icontains=buscar)
        ).distinct()
    
    # Filtro por categorías (permite múltiples)
    categorias_ids = request.GET.getlist('categoria')
    categorias_seleccionadas = []
    if categorias_ids:
        categorias_seleccionadas = Categoria.objects.filter(id__in=categorias_ids)
        productos_list = productos_list.filter(categoria__id__in=categorias_ids)
    
    # Filtro por marcas (permite múltiples)
    marcas_ids = request.GET.getlist('marca')
    marcas_seleccionadas = []
    if marcas_ids:
        marcas_seleccionadas = Marca.objects.filter(id__in=marcas_ids)
        productos_list = productos_list.filter(marca__id__in=marcas_ids)
    
    # Filtro por rango de precio
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    
    if precio_min:
        productos_list = productos_list.filter(precio__gte=Decimal(precio_min))
    if precio_max:
        productos_list = productos_list.filter(precio__lte=Decimal(precio_max))
    
    # Obtener rango de precios de todos los productos
    precios = Producto.objects.filter(esta_disponible=True).aggregate(
        min_precio=models.Min('precio'),
        max_precio=models.Max('precio')
    )
    precio_minimo_db = precios['min_precio'] or Decimal('0')
    precio_maximo_db = precios['max_precio'] or Decimal('100')
    
    # Ordenamiento
    orden = request.GET.get('orden', 'nombre')
    if orden == 'precio-asc':
        productos_list = productos_list.order_by('precio')
    elif orden == 'precio-desc':
        productos_list = productos_list.order_by('-precio')
    elif orden == 'destacados':
        productos_list = productos_list.order_by('-es_destacado', 'nombre')
    else:
        productos_list = productos_list.order_by('nombre')
    
    # Obtener todas las categorías y marcas para los filtros (solo las que tienen productos disponibles)
    categorias = Categoria.objects.filter(productos__esta_disponible=True).distinct()
    marcas = Marca.objects.filter(productos__esta_disponible=True).distinct()
    
    # Crear lista de IDs seleccionados para facilitar en el template
    categorias_ids_seleccionadas = [int(id) for id in categorias_ids]
    marcas_ids_seleccionadas = [int(id) for id in marcas_ids]
    
    contexto = {
        'productos': productos_list,
        'categorias': categorias,
        'marcas': marcas,
        'categorias_seleccionadas': categorias_seleccionadas,
        'marcas_seleccionadas': marcas_seleccionadas,
        'categorias_ids_seleccionadas': categorias_ids_seleccionadas,
        'marcas_ids_seleccionadas': marcas_ids_seleccionadas,
        'buscar': buscar,
        'orden': orden,
        'precio_min': precio_min or '',
        'precio_max': precio_max or '',
        'precio_minimo_db': float(precio_minimo_db),
        'precio_maximo_db': float(precio_maximo_db),
        'cart_info': obtener_info_carrito(request),
        'user_is_admin': es_usuario_admin(request)
    }
    
    return render(request, 'productos.html', contexto)

def producto_detalle(request, producto_id):
    """Vista de detalle de un producto"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Obtener productos relacionados de la misma categoría
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        esta_disponible=True
    ).exclude(id=producto.id)[:4]
    
    contexto = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
        'cart_info': obtener_info_carrito(request),
        'user_is_admin': es_usuario_admin(request)
    }
    
    return render(request, 'producto_detalle.html', contexto)

def carrito(request):
    """Vista del carrito de compras"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    cliente_id = request.session.get('cliente_id')
    
    # Si no hay cliente logueado, crear uno temporal para esta sesión
    if not cliente_id:
        # Verificar si ya tiene un carrito_temporal_id en la sesión
        carrito_temp_id = request.session.get('carrito_temporal_id')
        if not carrito_temp_id:
            # Crear cliente temporal para esta sesión específica
            import uuid
            temp_email = f'temp_{uuid.uuid4().hex[:12]}@temporal.local'
            invitado_temp = Cliente.objects.create(
                nombre='Invitado',
                apellidos='Temporal',
                email=temp_email,
                telefono='000000000',
                direccion='N/A',
                ciudad='N/A',
                codigo_postal='00000',
                password=''
            )
            request.session['cliente_id'] = invitado_temp.id
            request.session['es_invitado'] = True
            cliente_id = invitado_temp.id
        else:
            cliente_id = carrito_temp_id
            request.session['cliente_id'] = cliente_id
            request.session['es_invitado'] = True
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        # Si es la cuenta de invitado del sistema, crear uno temporal
        if cliente.email == EMAIL_INVITADO_SISTEMA:
            import uuid
            temp_email = f'temp_{uuid.uuid4().hex[:12]}@temporal.local'
            invitado_temp = Cliente.objects.create(
                nombre='Invitado',
                apellidos='Temporal',
                email=temp_email,
                telefono='000000000',
                direccion='N/A',
                ciudad='N/A',
                codigo_postal='00000',
                password=''
            )
            request.session['cliente_id'] = invitado_temp.id
            request.session['es_invitado'] = True
            cliente = invitado_temp
    except Cliente.DoesNotExist:
        request.session.flush()
        return redirect('mainPage')
    
    # Obtener o crear carrito para el cliente
    carrito_obj, created = Carrito.objects.get_or_create(cliente=cliente)
    
    # Calcular totales
    items = carrito_obj.items.all()
    subtotal = Decimal('0.00')
    
    items_con_total = []
    for item in items:
        precio = item.producto.precio
        total_item = (precio * item.cantidad).quantize(Decimal('0.01'))
        subtotal += total_item
        items_con_total.append({
            'item': item,
            'precio_unitario': precio,
            'total': total_item
        })
    
    iva = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))  # 21% IVA
    coste_envio = calcular_coste_envio(subtotal)
    total = (subtotal + iva + coste_envio).quantize(Decimal('0.01'))
    
    contexto = {
        'items': items_con_total,
        'subtotal': subtotal.quantize(Decimal('0.01')),
        'iva': iva,
        'coste_envio': coste_envio,
        'total': total,
        'cliente': cliente,
    }
    
    return render(request, 'carrito.html', contexto)

def agregar_al_carrito(request, producto_id):
    """Agregar producto al carrito"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    cliente_id = request.session.get('cliente_id')
    
    # Obtener la cantidad del parámetro GET (por defecto 1)
    try:
        cantidad = int(request.GET.get('cantidad', 1))
        if cantidad < 1:
            cantidad = 1
    except (ValueError, TypeError):
        cantidad = 1
    
    # Si no hay cliente logueado, crear uno temporal para esta sesión
    if not cliente_id:
        import uuid
        temp_email = f'temp_{uuid.uuid4().hex[:12]}@temporal.local'
        invitado_temp = Cliente.objects.create(
            nombre='Invitado',
            apellidos='Temporal',
            email=temp_email,
            telefono='000000000',
            direccion='N/A',
            ciudad='N/A',
            codigo_postal='00000',
            password=''
        )
        request.session['cliente_id'] = invitado_temp.id
        request.session['es_invitado'] = True
        cliente_id = invitado_temp.id
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        # Si es la cuenta compartida, crear uno temporal
        if cliente.email == EMAIL_INVITADO_SISTEMA:
            import uuid
            temp_email = f'temp_{uuid.uuid4().hex[:12]}@temporal.local'
            invitado_temp = Cliente.objects.create(
                nombre='Invitado',
                apellidos='Temporal',
                email=temp_email,
                telefono='000000000',
                direccion='N/A',
                ciudad='N/A',
                codigo_postal='00000',
                password=''
            )
            request.session['cliente_id'] = invitado_temp.id
            request.session['es_invitado'] = True
            cliente = invitado_temp
    except Cliente.DoesNotExist:
        request.session.flush()
        return redirect('mainPage')
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Validar que la cantidad no supere el stock disponible
    if cantidad > producto.stock:
        cantidad = producto.stock
    
    # Obtener o crear carrito
    carrito_obj, created = Carrito.objects.get_or_create(cliente=cliente)
    
    # Verificar si el producto ya está en el carrito
    item_carrito, created = ItemCarrito.objects.get_or_create(
        carrito=carrito_obj,
        producto=producto,
        defaults={'cantidad': cantidad}
    )
    
    if not created:
        # Si ya existe, verificar que no supere el stock
        nueva_cantidad = item_carrito.cantidad + cantidad
        if nueva_cantidad > producto.stock:
            # Ajustar a la cantidad máxima disponible
            nueva_cantidad = producto.stock
        item_carrito.cantidad = nueva_cantidad
        item_carrito.save()
    else:
        # Si es nuevo, verificar que haya stock disponible
        if producto.stock < 1:
            item_carrito.delete()
            return redirect('productos')
    
    # Obtener la URL de referencia o redirigir a productos
    referer = request.META.get('HTTP_REFERER')
    if referer and 'productos' in referer:
        return redirect('productos')
    return redirect('productos')

def comprar_ahora(request, producto_id):
    """Agregar producto al carrito y redirigir al carrito para compra inmediata"""
    cliente_id = request.session.get('cliente_id')
    
    # Obtener la cantidad del parámetro GET (por defecto 1)
    try:
        cantidad = int(request.GET.get('cantidad', 1))
        if cantidad < 1:
            cantidad = 1
    except (ValueError, TypeError):
        cantidad = 1
    
    # Si no hay cliente logueado, crear uno temporal para esta sesión
    if not cliente_id:
        import uuid
        temp_email = f'temp_{uuid.uuid4().hex[:12]}@temporal.local'
        invitado_temp = Cliente.objects.create(
            nombre='Invitado',
            apellidos='Temporal',
            email=temp_email,
            telefono='000000000',
            direccion='N/A',
            ciudad='N/A',
            codigo_postal='00000',
            password=''
        )
        request.session['cliente_id'] = invitado_temp.id
        request.session['es_invitado'] = True
        cliente_id = invitado_temp.id
    
    # Verificar si el cliente existe
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        # Si es la cuenta compartida, crear uno temporal
        if cliente.email == EMAIL_INVITADO_SISTEMA:
            import uuid
            temp_email = f'temp_{uuid.uuid4().hex[:12]}@temporal.local'
            invitado_temp = Cliente.objects.create(
                nombre='Invitado',
                apellidos='Temporal',
                email=temp_email,
                telefono='000000000',
                direccion='N/A',
                ciudad='N/A',
                codigo_postal='00000',
                password=''
            )
            request.session['cliente_id'] = invitado_temp.id
            request.session['es_invitado'] = True
            cliente = invitado_temp
    except Cliente.DoesNotExist:
        request.session.flush()
        return redirect('mainPage')
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Validar que la cantidad no supere el stock disponible
    if cantidad > producto.stock:
        cantidad = producto.stock
    
    # Obtener o crear carrito
    carrito_obj, created = Carrito.objects.get_or_create(cliente=cliente)
    
    # Verificar si el producto ya está en el carrito
    item_carrito, created = ItemCarrito.objects.get_or_create(
        carrito=carrito_obj,
        producto=producto,
        defaults={'cantidad': cantidad}
    )
    
    if not created:
        # Si ya existe, verificar que no supere el stock
        nueva_cantidad = item_carrito.cantidad + cantidad
        if nueva_cantidad > producto.stock:
            # Ajustar a la cantidad máxima disponible
            nueva_cantidad = producto.stock
        item_carrito.cantidad = nueva_cantidad
        item_carrito.save()
    else:
        # Si es nuevo, verificar que haya stock disponible
        if producto.stock < 1:
            item_carrito.delete()
            return redirect('producto_detalle', producto_id=producto_id)
    
    # Siempre redirigir al carrito
    return redirect('carrito')

def actualizar_cantidad_carrito(request, item_id):
    """Actualizar cantidad de un item del carrito"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    if request.method == 'POST':
        cliente_id = request.session.get('cliente_id')
        
        if not cliente_id:
            return redirect('carrito')
        
        item = get_object_or_404(ItemCarrito, id=item_id)
        nueva_cantidad = int(request.POST.get('cantidad', 1))
        
        if nueva_cantidad > 0:
            # Validar que no supere el stock disponible
            if nueva_cantidad > item.producto.stock:
                # Limitar a stock disponible
                item.cantidad = item.producto.stock
            else:
                item.cantidad = nueva_cantidad
            item.save()
        else:
            item.delete()
    
    return redirect('carrito')

def eliminar_del_carrito(request, item_id):
    """Eliminar item del carrito"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('carrito')
    
    item = get_object_or_404(ItemCarrito, id=item_id)
    item.delete()
    
    return redirect('carrito')

def checkout(request):
    """Vista de checkout - Paso 1: Datos de envío"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    cliente_id = request.session.get('cliente_id')
    
    # Si no hay cliente, crear uno temporal
    if not cliente_id:
        import uuid
        temp_email = f'temp_{uuid.uuid4().hex[:12]}@temporal.local'
        invitado_temp = Cliente.objects.create(
            nombre='Invitado',
            apellidos='Temporal',
            email=temp_email,
            telefono='000000000',
            direccion='N/A',
            ciudad='N/A',
            codigo_postal='00000',
            password=''
        )
        request.session['cliente_id'] = invitado_temp.id
        request.session['es_invitado'] = True
        cliente_id = invitado_temp.id
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        # Si es la cuenta compartida, crear uno temporal
        if cliente.email == EMAIL_INVITADO_SISTEMA:
            import uuid
            temp_email = f'temp_{uuid.uuid4().hex[:12]}@temporal.local'
            invitado_temp = Cliente.objects.create(
                nombre='Invitado',
                apellidos='Temporal',
                email=temp_email,
                telefono='000000000',
                direccion='N/A',
                ciudad='N/A',
                codigo_postal='00000',
                password=''
            )
            request.session['cliente_id'] = invitado_temp.id
            request.session['es_invitado'] = True
            cliente = invitado_temp
    except Cliente.DoesNotExist:
        request.session.flush()
        return redirect('mainPage')
    
    # Verificar si es invitado
    es_invitado = request.session.get('es_invitado', False) or cliente.email.endswith('@temporal.local') or cliente.email == EMAIL_INVITADO_SISTEMA
    
    try:
        carrito_obj = Carrito.objects.get(cliente=cliente)
    except Carrito.DoesNotExist:
        return redirect('carrito')
    
    items = carrito_obj.items.all()
    
    if not items:
        return redirect('carrito')
    
    # Calcular totales
    subtotal = Decimal('0.00')
    items_con_total = []
    
    for item in items:
        precio = item.producto.precio
        total_item = (precio * item.cantidad).quantize(Decimal('0.01'))
        subtotal += total_item
        items_con_total.append({
            'item': item,
            'precio_unitario': precio,
            'total': total_item
        })
    
    iva = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
    coste_envio = calcular_coste_envio(subtotal)
    total = (subtotal + iva + coste_envio).quantize(Decimal('0.01'))
    
    # Obtener método de pago favorito si no es invitado
    metodo_pago_favorito = 'tarjeta'
    if not es_invitado and hasattr(cliente, 'metodo_pago_favorito') and cliente.metodo_pago_favorito:
        metodo_pago_favorito = cliente.metodo_pago_favorito
    
    contexto = {
        'items': items_con_total,
        'subtotal': subtotal.quantize(Decimal('0.01')),
        'iva': iva,
        'coste_envio': coste_envio,
        'total': total,
        'cliente': cliente,
        'es_invitado': es_invitado,
        'paso_actual': 1,
        'metodo_pago_favorito': metodo_pago_favorito,
    }
    
    return render(request, 'checkout.html', contexto)

def checkout_paso2(request):
    """Paso 2: Guardar datos de envío y mostrar métodos de pago"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    if request.method != 'POST':
        return redirect('checkout')
    
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        invitado = obtener_invitado_sistema()
        request.session['cliente_id'] = invitado.id
        request.session['es_invitado'] = True
        cliente_id = invitado.id
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        request.session.flush()
        return redirect('mainPage')
    
    # Verificar si es invitado
    es_invitado = request.session.get('es_invitado', False) or cliente.email == EMAIL_INVITADO_SISTEMA
    
    # Guardar datos de envío en sesión, usando datos del cliente como predeterminados
    request.session['datos_envio'] = {
        'nombre': request.POST.get('nombre', '') or cliente.nombre,
        'apellidos': request.POST.get('apellidos', '') or cliente.apellidos,
        'email': request.POST.get('email', '') or cliente.email,
        'direccion': request.POST.get('direccion', ''),
        'ciudad': request.POST.get('ciudad', ''),
        'codigo_postal': request.POST.get('codigo_postal', ''),
        'telefono': request.POST.get('telefono', '') or cliente.telefono,
        'tipo_entrega': request.POST.get('tipo_entrega', 'domicilio'),
    }
    
    try:
        carrito_obj = Carrito.objects.get(cliente=cliente)
    except Carrito.DoesNotExist:
        return redirect('carrito')
    
    items = carrito_obj.items.all()
    
    # Calcular totales
    subtotal = Decimal('0.00')
    items_con_total = []
    
    for item in items:
        precio = item.producto.precio
        total_item = (precio * item.cantidad).quantize(Decimal('0.01'))
        subtotal += total_item
        items_con_total.append({
            'item': item,
            'precio_unitario': precio,
            'total': total_item
        })
    
    iva = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
    coste_envio = calcular_coste_envio(subtotal)
    total = (subtotal + iva + coste_envio).quantize(Decimal('0.01'))
    
    # Generar token de cliente para Braintree Drop-in UI
    try:
        client_token = gateway.client_token.generate()
    except Exception as e:
        client_token = None
        print(f"Error generando Braintree token: {e}")
    
    # Obtener método de pago favorito si no es invitado
    metodo_pago_favorito = 'tarjeta'
    if not es_invitado and hasattr(cliente, 'metodo_pago_favorito') and cliente.metodo_pago_favorito:
        metodo_pago_favorito = cliente.metodo_pago_favorito
    
    contexto = {
        'items': items_con_total,
        'subtotal': subtotal.quantize(Decimal('0.01')),
        'iva': iva,
        'coste_envio': coste_envio,
        'total': total,
        'cliente': cliente,
        'paso_actual': 2,
        'datos_envio': request.session.get('datos_envio', {}),
        'braintree_client_token': client_token,
        'metodo_pago_favorito': metodo_pago_favorito,
    }
    
    return render(request, 'checkout_paso2.html', contexto)

def checkout_paso3(request):
    """Paso 3: Confirmar pedido antes de procesar pago"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    if request.method != 'POST':
        return redirect('checkout')
    
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('carrito')
    
    # Guardar método de pago en sesión
    request.session['metodo_pago'] = request.POST.get('metodo_pago', 'tarjeta')
    
    # Guardar payment_method_nonce si viene de Braintree
    payment_nonce = request.POST.get('payment_method_nonce')
    if payment_nonce:
        request.session['payment_method_nonce'] = payment_nonce
    
    # Verificar si el cliente existe
    try:
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        return redirect('carrito')
    
    # Verificar si es invitado
    es_invitado = request.session.get('es_invitado', False) or cliente.email == EMAIL_INVITADO_SISTEMA
    
    try:
        carrito_obj = Carrito.objects.get(cliente=cliente)
    except Carrito.DoesNotExist:
        return redirect('carrito')
    
    items = carrito_obj.items.all()
    
    # Calcular totales
    subtotal = Decimal('0.00')
    items_con_total = []
    
    for item in items:
        precio = item.producto.precio
        total_item = (precio * item.cantidad).quantize(Decimal('0.01'))
        subtotal += total_item
        items_con_total.append({
            'item': item,
            'precio_unitario': precio,
            'total': total_item
        })
    
    iva = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
    coste_envio = calcular_coste_envio(subtotal)
    total = (subtotal + iva + coste_envio).quantize(Decimal('0.01'))
    
    contexto = {
        'items': items_con_total,
        'subtotal': subtotal.quantize(Decimal('0.01')),
        'iva': iva,
        'coste_envio': coste_envio,
        'total': total,
        'cliente': cliente,
        'es_invitado': es_invitado,
        'paso_actual': 3,
        'datos_envio': request.session.get('datos_envio', {}),
        'metodo_pago': request.session.get('metodo_pago', 'tarjeta'),
    }
    
    return render(request, 'checkout_paso3.html', contexto)

def procesar_pago(request):
    """Procesar el pago con Braintree o contra reembolso"""
    if request.method != 'POST':
        return redirect('checkout')
    
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    # Verificar si el cliente existe
    try:
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        return redirect('carrito')
    
    carrito_obj = get_object_or_404(Carrito, cliente=cliente)
    
    items = carrito_obj.items.all()
    
    if not items:
        return redirect('carrito')
    
    # Calcular totales
    subtotal = Decimal('0.00')
    for item in items:
        precio = item.producto.precio
        subtotal += (precio * item.cantidad).quantize(Decimal('0.01'))
    
    subtotal = subtotal.quantize(Decimal('0.01'))
    iva = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
    coste_envio = calcular_coste_envio(subtotal)
    descuento = Decimal('0.00')
    total = (subtotal + iva + coste_envio - descuento).quantize(Decimal('0.01'))
    
    # Obtener método de pago
    metodo_pago = request.session.get('metodo_pago', 'tarjeta')
    
    # Procesar según método de pago
    if metodo_pago == 'reembolso':
        # Contra reembolso: no procesar pago, solo crear pedido
        resultado_pago = {
            'success': True,
            'transaction_id': None,
            'estado': 'pending_cash_on_delivery'
        }
    else:
        # Pago con tarjeta: procesar con Braintree
        payment_method_nonce = request.session.get('payment_method_nonce')
        
        if not payment_method_nonce:
            request.session['error_pago'] = 'No se recibió el método de pago. Por favor, intenta nuevamente.'
            return redirect('checkout_paso3')
        
        # Procesar transacción con Braintree
        try:
            result = gateway.transaction.sale({
                'amount': str(total),
                'payment_method_nonce': payment_method_nonce,
                'options': {
                    'submit_for_settlement': True
                }
            })
            
            if result.is_success:
                resultado_pago = {
                    'success': True,
                    'transaction_id': result.transaction.id,
                    'estado': result.transaction.status
                }
            else:
                # Error en el pago
                request.session['error_pago'] = result.message
                return redirect('checkout_paso3')
        except Exception as e:
            request.session['error_pago'] = f"Error procesando pago: {str(e)}"
            return redirect('checkout_paso3')
    
    # Obtener datos de la sesión
    datos_envio = request.session.get('datos_envio', {})
    tipo_entrega = datos_envio.get('tipo_entrega', 'domicilio')
    metodo_pago = request.session.get('metodo_pago', 'tarjeta')
    
    # Construir dirección de envío según tipo de entrega
    if tipo_entrega == 'tienda':
        direccion_envio = "Recogida en tienda"
    else:
        direccion_envio = f"{cliente.direccion}, {cliente.ciudad}, {cliente.codigo_postal}"
    
    telefono = cliente.telefono
    
    # Determinar estado inicial según método de pago
    estado_pedido = determinar_estado_pedido(metodo_pago)
    
    # Crear el pedido con el estado adecuado
    numero_pedido = f"PED-{uuid.uuid4().hex[:8].upper()}"
    
    pedido = Pedido.objects.create(
        cliente=cliente,
        numero_pedido=numero_pedido,
        token_confirmacion=None,  # NULL porque no requiere confirmación manual
        subtotal=subtotal,
        impuestos=iva,
        coste_entrega=coste_envio,
        descuento=descuento,
        total=total,
        metodo_pago=metodo_pago,
        tipo_entrega=tipo_entrega,
        direccion_envio=direccion_envio,
        telefono=telefono,
        estado=estado_pedido  # 'confirmado' para tarjeta, 'en_espera_pago' para reembolso
    )
    
    # Crear items del pedido y REDUCIR STOCK INMEDIATAMENTE
    for item in items:
        precio = item.producto.precio
        total_item = (precio * item.cantidad).quantize(Decimal('0.01'))
        
        ItemPedido.objects.create(
            pedido=pedido,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=precio,
            total=total_item
        )
        
        # REDUCIR STOCK INMEDIATAMENTE
        producto = item.producto
        producto.stock -= item.cantidad
        if producto.stock < 0:
            producto.stock = 0
        producto.save()
    
    # Vaciar el carrito
    items.delete()
    
    # Enviar email informativo (sin lógica de confirmación)
    enviar_email_pedido_confirmado_rapido(pedido, request)
    
    # Limpiar datos de sesión
    if 'datos_envio' in request.session:
        del request.session['datos_envio']
    if 'metodo_pago' in request.session:
        del request.session['metodo_pago']
    if 'payment_method_nonce' in request.session:
        del request.session['payment_method_nonce']
    
    # Marcar pedido como confirmado en sesión
    request.session['pedido_confirmado'] = True
    
    # Redirigir a página de confirmación con el ID del pedido
    return redirect('confirmacion_pedido', pedido_id=pedido.id)

def confirmacion_pedido(request, pedido_id):
    """Vista de confirmación del pedido"""
    cliente_id = request.session.get('cliente_id')
    
    # Intentar obtener el pedido
    try:
        if cliente_id:
            pedido = get_object_or_404(Pedido, id=pedido_id, cliente_id=cliente_id)
            cliente = Cliente.objects.get(id=cliente_id)
            # Verificar si fue invitado
            fue_invitado = request.session.get('es_invitado', False) or cliente.email == EMAIL_INVITADO_SISTEMA
        else:
            # Permitir ver el pedido si acaba de ser creado en esta sesión
            pedido = get_object_or_404(Pedido, id=pedido_id)
            fue_invitado = True
    except:
        return redirect('mainPage')
    
    items = pedido.items.all()
    
    contexto = {
        'pedido': pedido,
        'items': items,
        'fue_invitado': fue_invitado,
    }
    
    return render(request, 'confirmacion_pedido.html', contexto)

def historial_pedidos(request):
    """Vista del historial de pedidos del cliente"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('mainPage')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        request.session.flush()
        return redirect('mainPage')
    
    # Verificar si es invitado
    es_invitado = request.session.get('es_invitado', False) or cliente.email == EMAIL_INVITADO_SISTEMA
    
    # Obtener todos los pedidos del cliente ordenados por fecha (más reciente primero)
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_creacion')
    
    # Preparar datos de los pedidos con sus items
    pedidos_con_items = []
    for pedido in pedidos:
        items = pedido.items.all()
        pedidos_con_items.append({
            'pedido': pedido,
            'items': items,
            'cantidad_items': sum(item.cantidad for item in items)
        })
    
    contexto = {
        'cliente': cliente,
        'pedidos_con_items': pedidos_con_items,
        'es_invitado': es_invitado,
    }
    
    return render(request, 'historial_pedidos.html', contexto)

def enviar_email_confirmacion(pedido):
    """Enviar email de confirmación del pedido al cliente"""
    try:
        asunto = f'Confirmación de Pedido #{pedido.numero_pedido} - Todo Jardin'
        
        # Obtener items del pedido
        items = pedido.items.all()
        
        # Preparar contexto para el email
        contexto = {
            'pedido': pedido,
            'items': items,
            'cliente': pedido.cliente,
        }
        
        # Crear mensaje HTML y texto plano
        mensaje_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a7c2c;">¡Gracias por tu compra en Todo Jardin!</h2>
                
                <p>Hola {pedido.cliente.nombre},</p>
                
                <p>Hemos recibido tu pedido correctamente. A continuación encontrarás los detalles:</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #4a7c2c; margin-top: 0;">Pedido #{pedido.numero_pedido}</h3>
                    <p><strong>Fecha:</strong> {pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>Estado:</strong> {pedido.get_estado_display()}</p>
                    <p><strong>Método de pago:</strong> {pedido.get_metodo_pago_display()}</p>
                </div>
                
                <h3 style="color: #4a7c2c;">Productos:</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr style="background-color: #f5f5f5;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #4a7c2c;">Producto</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #4a7c2c;">Cantidad</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #4a7c2c;">Precio</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for item in items:
            mensaje_html += f"""
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item.producto.nombre}</td>
                            <td style="padding: 10px; text-align: center; border-bottom: 1px solid #ddd;">{item.cantidad}</td>
                            <td style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">€{item.total}</td>
                        </tr>
            """
        
        mensaje_html += f"""
                    </tbody>
                </table>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                    <p style="margin: 5px 0;"><strong>Subtotal:</strong> €{pedido.subtotal}</p>
                    <p style="margin: 5px 0;"><strong>IVA (21%):</strong> €{pedido.impuestos}</p>
                    <p style="margin: 5px 0;"><strong>Envío:</strong> {"GRATIS" if pedido.coste_entrega == 0 else f"€{pedido.coste_entrega}"}</p>
                    <h3 style="color: #4a7c2c; margin: 10px 0;"><strong>Total:</strong> €{pedido.total}</h3>
                </div>
                
                <h3 style="color: #4a7c2c;">Dirección de envío:</h3>
                <p>{pedido.direccion_envio}<br>
                Teléfono: {pedido.telefono}</p>
                
                <p style="margin-top: 30px;">Si tienes alguna pregunta sobre tu pedido, no dudes en contactarnos.</p>
                
                <p style="color: #666; font-size: 0.9em; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
                    Este es un mensaje automático, por favor no respondas a este correo.<br>
                    © 2025 Todo Jardin - Todos los derechos reservados
                </p>
            </div>
        </body>
        </html>
        """
        
        mensaje_texto = f"""
        ¡Gracias por tu compra en Todo Jardin!
        
        Hola {pedido.cliente.nombre},
        
        Hemos recibido tu pedido correctamente.
        
        Pedido #{pedido.numero_pedido}
        Fecha: {pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
        Estado: {pedido.get_estado_display()}
        
        Productos:
        """
        
        for item in items:
            mensaje_texto += f"\n- {item.producto.nombre} x{item.cantidad} - €{item.total}"
        
        mensaje_texto += f"""
        
        Subtotal: €{pedido.subtotal}
        IVA (21%): €{pedido.impuestos}
        Envío: {"GRATIS" if pedido.coste_entrega == 0 else f"€{pedido.coste_entrega}"}
        Total: €{pedido.total}
        
        Dirección de envío:
        {pedido.direccion_envio}
        Teléfono: {pedido.telefono}
        
        Si tienes alguna pregunta, no dudes en contactarnos.
        
        © 2025 Todo Jardin
        """
        
        # Enviar email
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[pedido.cliente.email],
            html_message=mensaje_html,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error al enviar email: {str(e)}")
        return False

def enviar_email_confirmacion_pedido(pedido, request):
    """Enviar email con enlace de confirmación del pedido"""
    try:
        from django.core.mail import EmailMultiAlternatives
        from email.mime.text import MIMEText
        from email.header import Header
        
        # Generar URL de confirmación con token
        dominio = request.get_host()
        protocolo = 'https' if request.is_secure() else 'http'
        url_confirmacion = f"{protocolo}://{dominio}/confirmar-pedido/{pedido.id}/?token={pedido.token_confirmacion}"
        
        asunto = f'Confirma tu Pedido #{pedido.numero_pedido} - Todo Jardin'
        
        # Obtener items del pedido
        items = pedido.items.all()
        
        # Crear mensaje HTML
        mensaje_html = f"""
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a7c2c;">¡Gracias por tu compra en Todo Jardin!</h2>
                
                <p>Hola {pedido.cliente.nombre},</p>
                
                <p>Hemos recibido tu pedido. <strong>Para completar tu compra y actualizar el inventario, necesitamos que confirmes tu pedido haciendo clic en el botón de abajo:</strong></p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{url_confirmacion}" style="background: linear-gradient(135deg, #4a7c2c 0%, #6ba83e 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 1.1rem; display: inline-block;">
                        Confirmar Pedido
                    </a>
                </div>
                
                <p style="color: #666; font-size: 0.9rem;">Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                <p style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all; font-size: 0.85rem;">
                    {url_confirmacion}
                </p>
                
                <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0; color: #856404;"><strong>⚠️ Importante:</strong> Tu pedido permanecerá en estado "Pendiente" hasta que lo confirmes. El stock no se actualizará hasta entonces.</p>
                </div>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #4a7c2c; margin-top: 0;">Resumen del Pedido #{pedido.numero_pedido}</h3>
                    <p><strong>Fecha:</strong> {pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>Estado:</strong> Pendiente de Confirmación</p>
                </div>
                
                <h3 style="color: #4a7c2c;">Productos:</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr style="background-color: #f5f5f5;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #4a7c2c;">Producto</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #4a7c2c;">Cantidad</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #4a7c2c;">Precio</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for item in items:
            mensaje_html += f"""
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item.producto.nombre}</td>
                            <td style="padding: 10px; text-align: center; border-bottom: 1px solid #ddd;">{item.cantidad}</td>
                            <td style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">€{item.total}</td>
                        </tr>
            """
        
        mensaje_html += f"""
                    </tbody>
                </table>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                    <p style="margin: 5px 0;"><strong>Subtotal:</strong> €{pedido.subtotal}</p>
                    <p style="margin: 5px 0;"><strong>IVA (21%):</strong> €{pedido.impuestos}</p>
                    <p style="margin: 5px 0;"><strong>Envío:</strong> {"GRATIS" if pedido.coste_entrega == 0 else f"€{pedido.coste_entrega}"}</p>
                    <h3 style="color: #4a7c2c; margin: 10px 0;"><strong>Total:</strong> €{pedido.total}</h3>
                </div>
                
                <h3 style="color: #4a7c2c;">Dirección de envío:</h3>
                <p>{pedido.direccion_envio}<br>
                Teléfono: {pedido.telefono}</p>
                
                <p style="color: #666; font-size: 0.9em; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
                    Este es un mensaje automático, por favor no respondas a este correo.<br>
                    © 2025 Todo Jardin - Todos los derechos reservados
                </p>
            </div>
        </body>
        </html>
        """
        
        mensaje_texto = f"""
        ¡Gracias por tu compra en Todo Jardin!
        
        Hola {pedido.cliente.nombre},
        
        Hemos recibido tu pedido. Para completar tu compra, necesitamos que confirmes tu pedido.
        
        CONFIRMA TU PEDIDO AQUÍ:
        {url_confirmacion}
        
        ⚠️ IMPORTANTE: Tu pedido permanecerá en estado "Pendiente" hasta que lo confirmes.
        
        Pedido #{pedido.numero_pedido}
        Fecha: {pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
        Estado: Pendiente de Confirmación
        
        Productos:
        """
        
        for item in items:
            mensaje_texto += f"\n- {item.producto.nombre} x{item.cantidad} - €{item.total}"
        
        mensaje_texto += f"""
        
        Subtotal: €{pedido.subtotal}
        IVA (21%): €{pedido.impuestos}
        Envío: {"GRATIS" if pedido.coste_entrega == 0 else f"€{pedido.coste_entrega}"}
        Total: €{pedido.total}
        
        Dirección de envío:
        {pedido.direccion_envio}
        Teléfono: {pedido.telefono}
        
        © 2025 Todo Jardin
        """
        
        # Enviar email con codificación UTF-8 explícita
        email = EmailMultiAlternatives(
            subject=asunto,
            body=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[pedido.cliente.email]
        )
        email.attach_alternative(mensaje_html, "text/html")
        email.encoding = 'utf-8'
        
        # Forzar UTF-8 en headers
        email.extra_headers = {
            'Content-Type': 'text/html; charset=utf-8',
        }
        
        email.send(fail_silently=False)
        
        return True
    except Exception as e:
        print(f"Error al enviar email de confirmación: {str(e)}")
        return False

def enviar_email_pedido_confirmado(pedido):
    """Enviar email notificando que el pedido fue confirmado exitosamente"""
    try:
        from django.core.mail import EmailMultiAlternatives
        
        asunto = f'Pedido Confirmado #{pedido.numero_pedido} - Todo Jardin'
        
        # Obtener items del pedido
        items = pedido.items.all()
        
        # Crear mensaje HTML
        mensaje_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="display: inline-block; width: 80px; height: 80px; background: linear-gradient(135deg, #4a7c2c 0%, #6ba83e 100%); border-radius: 50%; padding: 20px;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                    </div>
                </div>
                
                <h2 style="color: #4a7c2c; text-align: center;">¡Tu Pedido Ha Sido Confirmado!</h2>
                
                <p>Hola {pedido.cliente.nombre},</p>
                
                <p>Tu pedido <strong>#{pedido.numero_pedido}</strong> ha sido confirmado exitosamente. Ahora procederemos a prepararlo para su envío.</p>
                
                <div style="background-color: #e8f5e9; border-left: 4px solid #4a7c2c; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0; color: #2d5016;"><strong>✓ Confirmado</strong> - Tu pedido está siendo procesado</p>
                </div>
                
                <h3 style="color: #4a7c2c;">Resumen del Pedido:</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr style="background-color: #f5f5f5;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #4a7c2c;">Producto</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #4a7c2c;">Cantidad</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #4a7c2c;">Precio</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for item in items:
            mensaje_html += f"""
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item.producto.nombre}</td>
                            <td style="padding: 10px; text-align: center; border-bottom: 1px solid #ddd;">{item.cantidad}</td>
                            <td style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">€{item.total}</td>
                        </tr>
            """
        
        mensaje_html += f"""
                    </tbody>
                </table>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                    <h3 style="color: #4a7c2c; margin: 10px 0;"><strong>Total Pagado:</strong> €{pedido.total}</h3>
                </div>
                
                <h3 style="color: #4a7c2c;">Dirección de envío:</h3>
                <p>{pedido.direccion_envio}<br>
                Teléfono: {pedido.telefono}</p>
                
                <p>Te mantendremos informado sobre el estado de tu pedido.</p>
                
                <p style="color: #666; font-size: 0.9em; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
                    © 2025 Todo Jardin - Todos los derechos reservados
                </p>
            </div>
        </body>
        </html>
        """
        
        mensaje_texto = f"""
        ¡Tu Pedido Ha Sido Confirmado!
        
        Hola {pedido.cliente.nombre},
        
        Tu pedido #{pedido.numero_pedido} ha sido confirmado exitosamente.
        
        ✓ Confirmado - Tu pedido está siendo procesado
        
        Total Pagado: €{pedido.total}
        
        Dirección de envío:
        {pedido.direccion_envio}
        Teléfono: {pedido.telefono}
        
        Te mantendremos informado sobre el estado de tu pedido.
        
        © 2025 Todo Jardin
        """
        
        # Enviar email con codificación UTF-8 explícita
        email = EmailMultiAlternatives(
            subject=asunto,
            body=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[pedido.cliente.email]
        )
        email.attach_alternative(mensaje_html, "text/html")
        email.encoding = 'utf-8'
        
        # Forzar UTF-8 en headers
        email.extra_headers = {
            'Content-Type': 'text/html; charset=utf-8',
        }
        
        email.send(fail_silently=False)
        
        return True
    except Exception as e:
        print(f"Error al enviar email de pedido confirmado: {str(e)}")
        return False

def confirmar_pedido(request, pedido_id):
    """Confirmar pedido mediante token de email y actualizar stock"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    # Obtener token de la URL
    token = request.GET.get('token')
    
    if not token:
        # Si no hay token, verificar si está autenticado
        cliente_id = request.session.get('cliente_id')
        
        if not cliente_id:
            return redirect('login')
        
        pedido = get_object_or_404(Pedido, id=pedido_id, cliente_id=cliente_id)
    else:
        # Si hay token, validar sin requerir autenticación
        pedido = get_object_or_404(Pedido, id=pedido_id, token_confirmacion=token)
    
    # Verificar que el pedido esté en estado pendiente
    if pedido.estado != 'pendiente':
        # Si ya está confirmado, redirigir al historial o confirmación
        return redirect('confirmacion_pedido', pedido_id=pedido.id)
    
    # Verificar stock disponible para todos los items
    items = pedido.items.all()
    stock_insuficiente = []
    
    for item in items:
        if item.producto.stock < item.cantidad:
            stock_insuficiente.append(f"{item.producto.nombre} (disponible: {item.producto.stock}, solicitado: {item.cantidad})")
    
    if stock_insuficiente:
        # Si hay stock insuficiente, mostrar error
        contexto = {
            'pedido': pedido,
            'items': items,
            'error': f"Stock insuficiente para: {', '.join(stock_insuficiente)}",
        }
        return render(request, 'confirmacion_pedido.html', contexto)
    
    # Actualizar stock de cada producto
    for item in items:
        producto = item.producto
        producto.stock -= item.cantidad
        
        # Mantener el stock en 0 como mínimo
        if producto.stock < 0:
            producto.stock = 0
        
        producto.save()
    
    # Cambiar estado del pedido a confirmado
    pedido.estado = 'confirmado'
    pedido.save()
    
    # Enviar email de confirmación exitosa
    enviar_email_pedido_confirmado(pedido)
    
    # Autenticar al cliente si vino desde el email
    if token and not request.session.get('cliente_id'):
        request.session['cliente_id'] = pedido.cliente.id
        request.session['pedido_confirmado_email'] = True
    
    # Redirigir a confirmación con mensaje de éxito
    request.session['pedido_confirmado'] = True
    return redirect('confirmacion_pedido', pedido_id=pedido.id)

def buscar_pedido(request):
    """Vista para buscar pedidos por número sin estar registrado"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    pedido_encontrado = None
    error = None
    
    if request.method == 'POST':
        numero_pedido = request.POST.get('numero_pedido', '').strip().upper()
        
        if not numero_pedido:
            error = 'Por favor, ingresa un número de pedido'
        else:
            # Eliminar el prefijo #PED- o PED- si existe
            if numero_pedido.startswith('#'):
                numero_pedido = numero_pedido[1:]
            if not numero_pedido.startswith('PED-'):
                numero_pedido = f'PED-{numero_pedido}'
            
            try:
                pedido = Pedido.objects.get(numero_pedido=numero_pedido)
                items = pedido.items.all()
                pedido_encontrado = {
                    'pedido': pedido,
                    'items': items,
                    'cantidad_items': sum(item.cantidad for item in items)
                }
            except Pedido.DoesNotExist:
                error = f'No se encontró ningún pedido con el número {numero_pedido}'
    
    contexto = {
        'pedido_encontrado': pedido_encontrado,
        'error': error,
    }
    
    return render(request, 'buscar_pedido.html', contexto)

def checkout_rapido(request, producto_id):
    """Vista de checkout rápido - Todo en un solo paso"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Obtener la cantidad del parámetro GET (por defecto 1)
    try:
        cantidad = int(request.GET.get('cantidad', 1))
        if cantidad < 1:
            cantidad = 1
        # Verificar que no exceda el stock
        if cantidad > producto.stock:
            cantidad = producto.stock
    except (ValueError, TypeError):
        cantidad = 1
    
    # Verificar stock
    if producto.stock <= 0:
        return redirect('producto_detalle', producto_id=producto_id)
    
    # Obtener o crear cliente (igual que checkout normal)
    cliente_id = request.session.get('cliente_id')
    
    # Si no hay cliente, crear uno temporal
    if not cliente_id:
        import uuid
        temp_email = f'temp_{uuid.uuid4().hex[:12]}@temporal.local'
        invitado_temp = Cliente.objects.create(
            nombre='Invitado',
            apellidos='Temporal',
            email=temp_email,
            telefono='000000000',
            direccion='N/A',
            ciudad='N/A',
            codigo_postal='00000',
            password=''
        )
        request.session['cliente_id'] = invitado_temp.id
        request.session['es_invitado'] = True
        cliente_id = invitado_temp.id
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        # Si es la cuenta compartida, crear uno temporal
        if cliente.email == EMAIL_INVITADO_SISTEMA:
            import uuid
            temp_email = f'temp_{uuid.uuid4().hex[:12]}@temporal.local'
            invitado_temp = Cliente.objects.create(
                nombre='Invitado',
                apellidos='Temporal',
                email=temp_email,
                telefono='000000000',
                direccion='N/A',
                ciudad='N/A',
                codigo_postal='00000',
                password=''
            )
            request.session['cliente_id'] = invitado_temp.id
            request.session['es_invitado'] = True
            cliente = invitado_temp
    except Cliente.DoesNotExist:
        request.session.flush()
        return redirect('mainPage')
    
    # Verificar si es invitado
    es_invitado = request.session.get('es_invitado', False) or cliente.email.endswith('@temporal.local') or cliente.email == EMAIL_INVITADO_SISTEMA
    
    # Si es invitado, no pasar datos del cliente para que no se autorellenen
    cliente_datos = None if es_invitado else cliente
    
    # Calcular totales para la cantidad especificada
    precio = producto.precio
    subtotal = precio * cantidad
    iva = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
    coste_envio = calcular_coste_envio(subtotal)
    total = (subtotal + iva + coste_envio).quantize(Decimal('0.01'))
    config = ConfiguracionEnvio.get_configuracion()
    envio_falta = (config.envio_minimo_gratis - subtotal).quantize(Decimal('0.01')) if subtotal < config.envio_minimo_gratis else Decimal('0.00')
    
    # Generar token de Braintree
    try:
        client_token = gateway.client_token.generate()
    except Exception as e:
        client_token = None
        print(f"Error generando Braintree token: {e}")
    
    # Obtener método de pago favorito si no es invitado
    metodo_pago_favorito = 'tarjeta'
    if not es_invitado and hasattr(cliente, 'metodo_pago_favorito') and cliente.metodo_pago_favorito:
        metodo_pago_favorito = cliente.metodo_pago_favorito
    
    contexto = {
        'producto': producto,
        'cantidad': cantidad,
        'cliente': cliente_datos,
        'es_invitado': es_invitado,
        'subtotal': subtotal.quantize(Decimal('0.01')),
        'iva': iva,
        'coste_envio': coste_envio,
        'total': total,
        'envio_falta': envio_falta,
        'braintree_client_token': client_token,
        'metodo_pago_favorito': metodo_pago_favorito,
    }
    
    return render(request, 'checkout_rapido.html', contexto)

def procesar_checkout_rapido(request):
    """Procesar compra rápida - Crear pedido directamente en estado confirmado"""
    # Bloquear acceso de administradores
    admin_redirect = bloquear_acceso_admin(request)
    if admin_redirect:
        return admin_redirect
    
    if request.method != 'POST':
        return redirect('productos')
    
    # Obtener datos del formulario
    producto_id = request.POST.get('producto_id')
    cantidad = int(request.POST.get('cantidad', 1))
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Verificar stock
    if producto.stock < cantidad:
        contexto = {
            'producto': producto,
            'error_message': f'Stock insuficiente. Solo hay {producto.stock} unidades disponibles.',
            'cliente': None,
        }
        return render(request, 'checkout_rapido.html', contexto)
    
    # Obtener datos personales del formulario
    nombre = request.POST.get('nombre', '').strip()
    apellidos = request.POST.get('apellidos', '').strip()
    email = request.POST.get('email', '').strip()
    telefono = request.POST.get('telefono', '').strip()
    
    # Obtener datos de envío
    tipo_entrega = request.POST.get('tipo_entrega', 'domicilio')
    direccion = request.POST.get('direccion', '').strip() if tipo_entrega == 'domicilio' else 'Recogida en tienda'
    ciudad = request.POST.get('ciudad', '').strip() if tipo_entrega == 'domicilio' else 'N/A'
    codigo_postal = request.POST.get('codigo_postal', '').strip() if tipo_entrega == 'domicilio' else 'N/A'
    
    # Obtener método de pago
    metodo_pago = request.POST.get('metodo_pago', 'tarjeta')
    
    # Validar campos requeridos
    if not all([nombre, apellidos, email, telefono]):
        contexto = {
            'producto': producto,
            'error_message': 'Por favor, completa todos los campos obligatorios.',
            'cliente': None,
        }
        return render(request, 'checkout_rapido.html', contexto)
    
    # Procesar pago si es con tarjeta
    if metodo_pago == 'tarjeta':
        payment_method_nonce = request.POST.get('payment_method_nonce')
        
        if not payment_method_nonce:
            contexto = {
                'producto': producto,
                'error_message': 'No se recibió el método de pago. Por favor, intenta nuevamente.',
                'cliente': None,
            }
            return render(request, 'checkout_rapido.html', contexto)
        
        # Calcular total
        precio = producto.precio
        subtotal = (precio * cantidad).quantize(Decimal('0.01'))
        iva = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
        coste_envio = calcular_coste_envio(subtotal)
        total = (subtotal + iva + coste_envio).quantize(Decimal('0.01'))
        
        # Procesar transacción con Braintree
        try:
            result = gateway.transaction.sale({
                'amount': str(total),
                'payment_method_nonce': payment_method_nonce,
                'options': {
                    'submit_for_settlement': True
                }
            })
            
            if not result.is_success:
                contexto = {
                    'producto': producto,
                    'error_message': f'Error al procesar el pago: {result.message}',
                    'cliente': None,
                }
                return render(request, 'checkout_rapido.html', contexto)
        except Exception as e:
            contexto = {
                'producto': producto,
                'error_message': f'Error procesando pago: {str(e)}',
                'cliente': None,
            }
            return render(request, 'checkout_rapido.html', contexto)
    
    # Obtener cliente de la sesión
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        return redirect('login')
    
    # Calcular totales
    precio = producto.precio
    subtotal = (precio * cantidad).quantize(Decimal('0.01'))
    iva = (subtotal * Decimal('0.21')).quantize(Decimal('0.01'))
    coste_envio = calcular_coste_envio(subtotal)
    total = (subtotal + iva + coste_envio).quantize(Decimal('0.01'))
    
    # Crear dirección de envío
    if tipo_entrega == 'domicilio':
        direccion_envio = f"{direccion}, {ciudad}, {codigo_postal}"
    else:
        direccion_envio = "Recogida en tienda"
    
    # Determinar estado inicial según método de pago
    estado_pedido = determinar_estado_pedido(metodo_pago)
    
    # Crear el pedido con el estado adecuado
    numero_pedido = f"PED-{uuid.uuid4().hex[:8].upper()}"
    
    pedido = Pedido.objects.create(
        cliente=cliente,
        numero_pedido=numero_pedido,
        token_confirmacion=None,  # NULL porque no requiere confirmación manual
        subtotal=subtotal,
        impuestos=iva,
        coste_entrega=coste_envio,
        descuento=Decimal('0.00'),
        total=total,
        metodo_pago=metodo_pago,
        tipo_entrega=tipo_entrega,
        direccion_envio=direccion_envio,
        telefono=telefono,
        estado=estado_pedido  # 'confirmado' para tarjeta, 'en_espera_pago' para reembolso
    )
    
    # Crear item del pedido
    total_item = (precio * cantidad).quantize(Decimal('0.01'))
    
    ItemPedido.objects.create(
        pedido=pedido,
        producto=producto,
        cantidad=cantidad,
        precio_unitario=precio,
        total=total_item
    )
    
    # REDUCIR STOCK INMEDIATAMENTE
    producto.stock -= cantidad
    if producto.stock < 0:
        producto.stock = 0
    producto.save()
    
    # Enviar email informativo (sin lógica de confirmación)
    enviar_email_pedido_confirmado_rapido(pedido, request)
    
    # Redirigir a confirmación
    request.session['pedido_confirmado'] = True
    return redirect('confirmacion_pedido', pedido_id=pedido.id)

def enviar_email_pedido_confirmado_rapido(pedido, request):
    """Enviar email informativo de pedido confirmado (sin token de confirmación)"""
    try:
        from django.core.mail import EmailMultiAlternatives
        
        asunto = f'Pedido Confirmado #{pedido.numero_pedido} - Todo Jardin'
        
        # Obtener items del pedido
        items = pedido.items.all()
        
        # Crear mensaje HTML
        mensaje_html = f"""
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4a7c2c;">¡Gracias por tu compra en Todo Jardin!</h2>
                
                <p>Hola {pedido.cliente.nombre},</p>
                
                <p><strong>Tu pedido ha sido confirmado y está siendo procesado.</strong></p>
                
                <div style="background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0; color: #155724;"><strong>✓ Pedido Confirmado</strong><br>
                    Hemos actualizado nuestro inventario y tu pedido está en proceso de preparación.</p>
                </div>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #4a7c2c; margin-top: 0;">Resumen del Pedido #{pedido.numero_pedido}</h3>
                    <p><strong>Fecha:</strong> {pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>Estado:</strong> Confirmado</p>
                    <p><strong>Método de pago:</strong> {pedido.get_metodo_pago_display()}</p>
                    <p><strong>Tipo de entrega:</strong> {pedido.get_tipo_entrega_display()}</p>
                </div>
                
                <h3 style="color: #4a7c2c;">Productos:</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr style="background-color: #f5f5f5;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #4a7c2c;">Producto</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #4a7c2c;">Cantidad</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #4a7c2c;">Precio</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for item in items:
            mensaje_html += f"""
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item.producto.nombre}</td>
                            <td style="padding: 10px; text-align: center; border-bottom: 1px solid #ddd;">{item.cantidad}</td>
                            <td style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">€{item.total}</td>
                        </tr>
            """
        
        mensaje_html += f"""
                    </tbody>
                </table>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                    <p style="margin: 5px 0;"><strong>Subtotal:</strong> €{pedido.subtotal}</p>
                    <p style="margin: 5px 0;"><strong>IVA (21%):</strong> €{pedido.impuestos}</p>
                    <p style="margin: 5px 0;"><strong>Envío:</strong> {"GRATIS" if pedido.coste_entrega == 0 else f"€{pedido.coste_entrega}"}</p>
                    <h3 style="color: #4a7c2c; margin: 10px 0;"><strong>Total:</strong> €{pedido.total}</h3>
                </div>
                
                <h3 style="color: #4a7c2c;">Dirección de envío:</h3>
                <p>{pedido.direccion_envio}<br>
                Teléfono: {pedido.telefono}</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="color: #666;">Puedes consultar el estado de tu pedido usando el número:</p>
                    <p style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; font-size: 1.5rem; font-weight: bold; color: #4a7c2c;">
                        {pedido.numero_pedido}
                    </p>
                </div>
                
                <p style="color: #666; font-size: 0.9em; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
                    Este es un mensaje automático, por favor no respondas a este correo.<br>
                    © 2025 Todo Jardin - Todos los derechos reservados
                </p>
            </div>
        </body>
        </html>
        """
        
        mensaje_texto = f"""
        ¡Gracias por tu compra en Todo Jardin!
        
        Hola {pedido.cliente.nombre},
        
        Tu pedido ha sido confirmado y está siendo procesado.
        
        Resumen del Pedido #{pedido.numero_pedido}
        Fecha: {pedido.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
        Estado: Confirmado
        
        Productos:
        """
        
        for item in items:
            mensaje_texto += f"- {item.producto.nombre} x{item.cantidad} - €{item.total}\n"
        
        mensaje_texto += f"""
        
        Subtotal: €{pedido.subtotal}
        IVA (21%): €{pedido.impuestos}
        Envío: {"GRATIS" if pedido.coste_entrega == 0 else f"€{pedido.coste_entrega}"}
        Total: €{pedido.total}
        
        Dirección de envío:
        {pedido.direccion_envio}
        Teléfono: {pedido.telefono}
        
        Puedes consultar el estado de tu pedido usando el número: {pedido.numero_pedido}
        
        © 2025 Todo Jardin - Todos los derechos reservados
        """
        
        email = EmailMultiAlternatives(
            subject=asunto,
            body=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[pedido.cliente.email]
        )
        
        email.attach_alternative(mensaje_html, "text/html")
        email.send(fail_silently=False)
        
        print(f"Email informativo enviado a {pedido.cliente.email} para pedido {pedido.numero_pedido}")
        
    except Exception as e:
        print(f"Error enviando email informativo: {e}")


# Import admin views
from .views_admin import (
    admin_panel, admin_pedidos, admin_actualizar_estado_pedido, admin_eliminar_pedido,
    admin_productos, admin_crear_producto, admin_editar_producto, admin_eliminar_producto,
    admin_usuarios, admin_toggle_admin, admin_eliminar_usuario
)

