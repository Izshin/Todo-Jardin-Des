from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models
from django.db.models import Q
from .models import Cliente, Pedido, Producto, Categoria, Marca, ImagenProducto
from decimal import Decimal

# Admin Views
def admin_panel(request):
    """Panel principal de administración"""
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    total_pedidos = Pedido.objects.count()
    total_productos = Producto.objects.count()
    total_usuarios = Cliente.objects.count()
    
    contexto = {
        'total_pedidos': total_pedidos,
        'total_productos': total_productos,
        'total_usuarios': total_usuarios,
    }
    
    return render(request, 'admin_panel.html', contexto)


def admin_pedidos(request):
    """Gestión de pedidos"""
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    # Obtener parámetro de búsqueda
    buscar_pedido = request.GET.get('buscar_pedido', '').strip()
    
    # Filtrar pedidos
    pedidos = Pedido.objects.all()
    
    if buscar_pedido:
        # Normalizar búsqueda: si empieza con "PED-", quitarlo
        numero_busqueda = buscar_pedido.upper()
        if numero_busqueda.startswith('PED-'):
            numero_busqueda = numero_busqueda[4:]
        
        # Buscar por número de pedido (con o sin prefijo)
        pedidos = pedidos.filter(
            Q(numero_pedido__iexact=numero_busqueda) | 
            Q(numero_pedido__iexact=f'PED-{numero_busqueda}')
        )
    
    pedidos = pedidos.order_by('-fecha_creacion')
    
    contexto = {
        'pedidos': pedidos,
        'buscar_pedido': buscar_pedido,
    }
    
    return render(request, 'admin_pedidos.html', contexto)


def admin_actualizar_estado_pedido(request, pedido_id):
    """Actualizar estado de un pedido"""
    if request.method != 'POST':
        return redirect('admin_pedidos')
    
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    estado_anterior = pedido.estado
    nuevo_estado = request.POST.get('estado')
    
    if nuevo_estado in ['pendiente', 'confirmado', 'procesando', 'enviado', 'entregado', 'cancelado']:
        pedido.estado = nuevo_estado
        pedido.save()
        
        # Si el estado cambió de 'pendiente' a 'confirmado', reducir stock
        if estado_anterior == 'pendiente' and nuevo_estado == 'confirmado':
            for item in pedido.items.all():
                producto = item.producto
                producto.stock -= item.cantidad
                if producto.stock < 0:
                    producto.stock = 0
                producto.save()
    
    return redirect('admin_pedidos')


def admin_eliminar_pedido(request, pedido_id):
    """Eliminar un pedido"""
    if request.method != 'POST':
        return redirect('admin_pedidos')
    
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.delete()
    
    return redirect('admin_pedidos')


def admin_productos(request):
    """Gestión de productos"""
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    # Obtener min y max precio de todos los productos
    precio_stats = Producto.objects.aggregate(
        precio_minimo=models.Min('precio'),
        precio_maximo=models.Max('precio')
    )
    precio_minimo_global = int(precio_stats['precio_minimo'] or 0)
    precio_maximo_global = int(precio_stats['precio_maximo'] or 1000)
    
    # Obtener filtros
    buscar = request.GET.get('buscar', '')
    categorias_ids = request.GET.getlist('categoria')
    marcas_ids = request.GET.getlist('marca')
    precio_min = request.GET.get('precio_min', str(precio_minimo_global))
    precio_max = request.GET.get('precio_max', str(precio_maximo_global))
    
    # Convertir precios a Decimal
    try:
        precio_min = Decimal(precio_min)
    except:
        precio_min = Decimal(precio_minimo_global)
    
    try:
        precio_max = Decimal(precio_max)
    except:
        precio_max = Decimal(precio_maximo_global)
    
    # Filtrar productos
    productos = Producto.objects.all()
    
    if buscar:
        productos = productos.filter(
            models.Q(nombre__icontains=buscar) | 
            models.Q(descripcion__icontains=buscar)
        )
    
    if categorias_ids:
        productos = productos.filter(categoria_id__in=categorias_ids)
    
    if marcas_ids:
        productos = productos.filter(marca_id__in=marcas_ids)
    
    # Filtrar por precio
    productos = productos.filter(precio__gte=precio_min, precio__lte=precio_max)
    
    productos = productos.order_by('nombre')
    
    # Obtener todas las categorías y marcas para los filtros
    categorias = Categoria.objects.all()
    marcas = Marca.objects.all()
    
    # Convertir IDs a enteros para comparación en template
    categorias_ids_seleccionadas = [int(id) for id in categorias_ids]
    marcas_ids_seleccionadas = [int(id) for id in marcas_ids]
    
    contexto = {
        'productos': productos,
        'categorias': categorias,
        'marcas': marcas,
        'buscar': buscar,
        'categorias_ids_seleccionadas': categorias_ids_seleccionadas,
        'marcas_ids_seleccionadas': marcas_ids_seleccionadas,
        'precio_min': int(precio_min),
        'precio_max': int(precio_max),
        'precio_minimo_global': precio_minimo_global,
        'precio_maximo_global': precio_maximo_global,
    }
    
    return render(request, 'admin_productos.html', contexto)


def admin_crear_producto(request):
    """Crear nuevo producto"""
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = Decimal(request.POST.get('precio', '0'))
        stock = int(request.POST.get('stock', '0'))
        categoria_id = request.POST.get('categoria')
        marca_id = request.POST.get('marca')
        es_destacado = request.POST.get('es_destacado') == 'on'
        imagen = request.FILES.get('imagen')
        
        # Características del producto
        genero = request.POST.get('genero') or None
        color = request.POST.get('color', '').strip() or None
        material = request.POST.get('material', '').strip() or None
        
        # Manejar creación de nueva categoría
        nueva_categoria = request.POST.get('nueva_categoria', '').strip()
        if nueva_categoria:
            categoria = Categoria.objects.create(nombre=nueva_categoria)
        elif categoria_id:
            categoria = get_object_or_404(Categoria, id=categoria_id)
        else:
            categoria = None
        
        # Manejar creación de nueva marca
        nueva_marca = request.POST.get('nueva_marca', '').strip()
        if nueva_marca:
            marca = Marca.objects.create(nombre=nueva_marca)
        elif marca_id:
            marca = get_object_or_404(Marca, id=marca_id)
        else:
            marca = None
        
        producto = Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria=categoria,
            marca=marca,
            genero=genero,
            color=color,
            material=material,
            es_destacado=es_destacado,
            esta_disponible=True
        )
        
        # Crear imagen si se proporciona
        if imagen:
            ImagenProducto.objects.create(
                producto=producto,
                imagen=imagen,
                es_principal=True
            )
        
        return redirect('admin_productos')
    
    categorias = Categoria.objects.all()
    marcas = Marca.objects.all()
    
    contexto = {
        'categorias': categorias,
        'marcas': marcas,
    }
    
    return render(request, 'admin_crear_producto.html', contexto)


def admin_editar_producto(request, producto_id):
    """Editar producto existente"""
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion')
        producto.precio = Decimal(request.POST.get('precio', '0'))
        producto.stock = int(request.POST.get('stock', '0'))
        
        # Características del producto
        producto.genero = request.POST.get('genero') or None
        producto.color = request.POST.get('color', '').strip() or None
        producto.material = request.POST.get('material', '').strip() or None
        
        categoria_id = request.POST.get('categoria')
        marca_id = request.POST.get('marca')
        
        # Manejar creación de nueva categoría
        nueva_categoria = request.POST.get('nueva_categoria', '').strip()
        if nueva_categoria:
            producto.categoria = Categoria.objects.create(nombre=nueva_categoria)
        elif categoria_id:
            producto.categoria = get_object_or_404(Categoria, id=categoria_id)
        else:
            producto.categoria = None
        
        # Manejar creación de nueva marca
        nueva_marca = request.POST.get('nueva_marca', '').strip()
        if nueva_marca:
            producto.marca = Marca.objects.create(nombre=nueva_marca)
        elif marca_id:
            producto.marca = get_object_or_404(Marca, id=marca_id)
        else:
            producto.marca = None
        
        producto.es_destacado = request.POST.get('es_destacado') == 'on'
        producto.esta_disponible = request.POST.get('esta_disponible') == 'on'
        
        # Manejar nueva imagen si se proporciona
        imagen = request.FILES.get('imagen')
        if imagen:
            # Eliminar imagen anterior si existe
            ImagenProducto.objects.filter(producto=producto, es_principal=True).delete()
            # Crear nueva imagen
            ImagenProducto.objects.create(
                producto=producto,
                imagen=imagen,
                es_principal=True
            )
        
        producto.save()
        
        return redirect('admin_productos')
    
    categorias = Categoria.objects.all()
    marcas = Marca.objects.all()
    
    contexto = {
        'producto': producto,
        'categorias': categorias,
        'marcas': marcas,
    }
    
    return render(request, 'admin_editar_producto.html', contexto)


def admin_eliminar_producto(request, producto_id):
    """Eliminar un producto"""
    if request.method != 'POST':
        return redirect('admin_productos')
    
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Eliminar el producto (las imágenes asociadas se eliminarán automáticamente)
    producto.delete()
    
    return redirect('admin_productos')


def admin_usuarios(request):
    """Gestión de usuarios"""
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    # Excluir usuarios invitados (sin contraseña o con nombre 'Invitado')
    usuarios = Cliente.objects.exclude(
        Q(password='') | Q(password__isnull=True) | Q(nombre='Invitado')
    ).order_by('-fecha_creacion')
    
    contexto = {
        'usuarios': usuarios,
        'cliente_actual_id': cliente.id,
    }
    
    return render(request, 'admin_usuarios.html', contexto)


def admin_toggle_admin(request, usuario_id):
    """Otorgar o quitar permisos de administrador"""
    if request.method != 'POST':
        return redirect('admin_usuarios')
    
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    usuario = get_object_or_404(Cliente, id=usuario_id)
    
    # No permitir que se quite sus propios permisos
    if usuario.id == cliente.id:
        return redirect('admin_usuarios')
    
    usuario.is_admin = not usuario.is_admin
    usuario.save()
    
    return redirect('admin_usuarios')


def admin_eliminar_usuario(request, usuario_id):
    """Eliminar un usuario"""
    if request.method != 'POST':
        return redirect('admin_usuarios')
    
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    usuario = get_object_or_404(Cliente, id=usuario_id)
    
    # No permitir que se elimine a sí mismo
    if usuario.id == cliente.id:
        return redirect('admin_usuarios')
    
    usuario.delete()
    
    return redirect('admin_usuarios')


def admin_crear_usuario(request):
    """Crear un nuevo usuario"""
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        codigo_postal = request.POST.get('codigo_postal')
        password = request.POST.get('password')
        is_admin = request.POST.get('is_admin') == 'on'
        
        # Validar que el email no exista
        if Cliente.objects.filter(email=email).exists():
            contexto = {
                'error': 'Ya existe un usuario con este email',
                'email': email,
                'nombre': nombre,
                'apellidos': apellidos,
                'telefono': telefono,
                'direccion': direccion,
                'ciudad': ciudad,
                'codigo_postal': codigo_postal,
            }
            return render(request, 'admin_crear_usuario.html', contexto)
        
        # Crear usuario
        nuevo_usuario = Cliente.objects.create(
            email=email,
            nombre=nombre,
            apellidos=apellidos,
            telefono=telefono,
            direccion=direccion,
            ciudad=ciudad,
            codigo_postal=codigo_postal,
            password=password,
            is_admin=is_admin
        )
        
        return redirect('admin_usuarios')
    
    return render(request, 'admin_crear_usuario.html')


def admin_editar_usuario(request, usuario_id):
    """Editar un usuario existente"""
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        return redirect('login')
    
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        if not cliente.is_admin:
            return redirect('mainPage')
    except Cliente.DoesNotExist:
        return redirect('login')
    
    usuario = get_object_or_404(Cliente, id=usuario_id)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        nombre = request.POST.get('nombre')
        apellidos = request.POST.get('apellidos')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        codigo_postal = request.POST.get('codigo_postal')
        password = request.POST.get('password')
        is_admin = request.POST.get('is_admin') == 'on'
        
        # Validar que el email no exista en otro usuario
        if Cliente.objects.filter(email=email).exclude(id=usuario_id).exists():
            contexto = {
                'error': 'Ya existe otro usuario con este email',
                'usuario': usuario,
            }
            return render(request, 'admin_editar_usuario.html', contexto)
        
        # Actualizar usuario
        usuario.email = email
        usuario.nombre = nombre
        usuario.apellidos = apellidos
        usuario.telefono = telefono
        usuario.direccion = direccion
        usuario.ciudad = ciudad
        usuario.codigo_postal = codigo_postal
        
        # Solo actualizar contraseña si se proporciona una nueva
        if password:
            usuario.password = password
        
        # No permitir que se quite sus propios permisos de admin
        if usuario.id != cliente.id:
            usuario.is_admin = is_admin
        
        usuario.save()
        
        return redirect('admin_usuarios')
    
    contexto = {
        'usuario': usuario,
        'es_usuario_actual': usuario.id == cliente.id,
    }
    return render(request, 'admin_editar_usuario.html', contexto)
