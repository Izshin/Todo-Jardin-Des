from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
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
    
    pedidos = Pedido.objects.all().order_by('-fecha_creacion')
    
    contexto = {
        'pedidos': pedidos,
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
    
    productos = Producto.objects.all().order_by('nombre')
    
    contexto = {
        'productos': productos,
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
        precio_oferta = request.POST.get('precio_oferta')
        stock = int(request.POST.get('stock', '0'))
        categoria_id = request.POST.get('categoria')
        marca_id = request.POST.get('marca')
        es_destacado = request.POST.get('es_destacado') == 'on'
        imagen = request.FILES.get('imagen')
        
        categoria = get_object_or_404(Categoria, id=categoria_id) if categoria_id else None
        marca = get_object_or_404(Marca, id=marca_id) if marca_id else None
        
        producto = Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            precio_oferta=Decimal(precio_oferta) if precio_oferta else None,
            stock=stock,
            categoria=categoria,
            marca=marca,
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
        precio_oferta = request.POST.get('precio_oferta')
        producto.precio_oferta = Decimal(precio_oferta) if precio_oferta else None
        producto.stock = int(request.POST.get('stock', '0'))
        
        categoria_id = request.POST.get('categoria')
        marca_id = request.POST.get('marca')
        
        producto.categoria = get_object_or_404(Categoria, id=categoria_id) if categoria_id else None
        producto.marca = get_object_or_404(Marca, id=marca_id) if marca_id else None
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
    
    usuarios = Cliente.objects.all().order_by('-fecha_creacion')
    
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
