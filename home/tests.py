from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from .models import Cliente, Producto, Categoria, Marca, ImagenProducto, Carrito, ItemCarrito, Pedido, ItemPedido

class ClienteModelTests(TestCase):
    """Tests para el modelo Cliente"""
    
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre='Juan',
            apellidos='Pérez García',
            email='juan@test.com',
            telefono='612345678',
            direccion='Calle Test 123',
            ciudad='Sevilla',
            codigo_postal='41001',
            password='test123'
        )
    
    def test_crear_cliente(self):
        """Test crear un cliente correctamente"""
        self.assertEqual(self.cliente.nombre, 'Juan')
        self.assertEqual(self.cliente.email, 'juan@test.com')
        self.assertFalse(self.cliente.is_admin)
    
    def test_str_cliente(self):
        """Test representación string del cliente"""
        self.assertEqual(str(self.cliente), 'Juan Pérez García')


class ProductoModelTests(TestCase):
    """Tests para el modelo Producto"""
    
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nombre='Plantas',
            descripcion='Plantas de interior'
        )
        self.marca = Marca.objects.create(nombre='TodoJardin')
        self.producto = Producto.objects.create(
            nombre='Cactus',
            descripcion='Cactus pequeño',
            precio=Decimal('9.99'),
            marca=self.marca,
            categoria=self.categoria,
            stock=10,
            esta_disponible=True
        )
    
    def test_crear_producto(self):
        """Test crear un producto correctamente"""
        self.assertEqual(self.producto.nombre, 'Cactus')
        self.assertEqual(self.producto.precio, Decimal('9.99'))
        self.assertEqual(self.producto.stock, 10)
        self.assertTrue(self.producto.esta_disponible)
    
    def test_producto_con_oferta(self):
        """Test producto con precio de oferta"""
        self.producto.precio_oferta = Decimal('7.99')
        self.producto.save()
        self.assertEqual(self.producto.precio_oferta, Decimal('7.99'))


class ViewsTests(TestCase):
    """Tests para las vistas principales"""
    
    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nombre='Plantas')
        self.marca = Marca.objects.create(nombre='TodoJardin')
        self.producto = Producto.objects.create(
            nombre='Cactus Test',
            precio=Decimal('15.00'),
            marca=self.marca,
            categoria=self.categoria,
            stock=5,
            esta_disponible=True
        )
    
    def test_pagina_principal(self):
        """Test que la página principal carga correctamente"""
        response = self.client.get(reverse('mainPage'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Todo Jardin')
    
    def test_pagina_productos(self):
        """Test que la página de productos carga"""
        response = self.client.get(reverse('productos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cactus Test')
    
    def test_detalle_producto(self):
        """Test que se puede ver el detalle de un producto"""
        response = self.client.get(reverse('producto_detalle', args=[self.producto.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cactus Test')
    
    def test_pagina_login(self):
        """Test que la página de login carga"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_pagina_registro(self):
        """Test que la página de registro carga"""
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)


class CarritoTests(TestCase):
    """Tests para funcionalidad del carrito"""
    
    def setUp(self):
        self.client = Client()
        self.cliente = Cliente.objects.create(
            nombre='Test',
            apellidos='User',
            email='test@test.com',
            telefono='600000000',
            direccion='Test 123',
            ciudad='Sevilla',
            codigo_postal='41001',
            password='test123'
        )
        self.categoria = Categoria.objects.create(nombre='Plantas')
        self.marca = Marca.objects.create(nombre='TodoJardin')
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            precio=Decimal('20.00'),
            marca=self.marca,
            categoria=self.categoria,
            stock=10,
            esta_disponible=True
        )
    
    def test_ver_carrito(self):
        """Test que se puede ver el carrito"""
        response = self.client.get(reverse('carrito'))
        self.assertEqual(response.status_code, 200)
    
    def test_agregar_producto_al_carrito(self):
        """Test agregar producto al carrito"""
        session = self.client.session
        session['cliente_id'] = self.cliente.id
        session.save()
        
        # Agregar dos veces el mismo producto
        self.client.post(reverse('agregar_al_carrito', args=[self.producto.id]))
        self.client.post(reverse('agregar_al_carrito', args=[self.producto.id]))
        
        # Verificar que se creó el item en el carrito con cantidad 2
        carrito = Carrito.objects.get(cliente=self.cliente)
        item = carrito.items.first()
        self.assertIsNotNone(item)
        self.assertEqual(item.cantidad, 2)


class BuscarPedidoTests(TestCase):
    """Tests para la funcionalidad de buscar pedido"""
    
    def setUp(self):
        self.client = Client()
        self.cliente = Cliente.objects.create(
            nombre='Cliente',
            apellidos='Test',
            email='cliente@test.com',
            telefono='600000000',
            direccion='Test',
            ciudad='Sevilla',
            codigo_postal='41001',
            password='test123'
        )
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            numero_pedido='PED-TEST123',
            subtotal=Decimal('50.00'),
            impuestos=Decimal('10.50'),
            coste_entrega=Decimal('5.99'),
            total=Decimal('66.49'),
            estado='pendiente',
            metodo_pago='tarjeta',
            direccion_envio='Calle Test 123, Sevilla, 41001',
            telefono='600000000'
        )
    
    def test_pagina_buscar_pedido(self):
        """Test que la página de buscar pedido carga"""
        response = self.client.get(reverse('buscar_pedido'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buscar Mi Pedido')
    
    def test_buscar_pedido_existente(self):
        """Test buscar un pedido que existe"""
        response = self.client.post(
            reverse('buscar_pedido'),
            {'numero_pedido': 'PED-TEST123'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PED-TEST123')
    
    def test_buscar_pedido_sin_prefijo(self):
        """Test buscar pedido sin el prefijo PED-"""
        response = self.client.post(
            reverse('buscar_pedido'),
            {'numero_pedido': 'TEST123'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PED-TEST123')
    
    def test_buscar_pedido_inexistente(self):
        """Test buscar un pedido que no existe"""
        response = self.client.post(
            reverse('buscar_pedido'),
            {'numero_pedido': 'PED-NOEXISTE'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No se encontró')


class AutenticacionTests(TestCase):
    """Tests para autenticación de usuarios"""
    
    def setUp(self):
        self.client = Client()
        self.cliente = Cliente.objects.create(
            nombre='Usuario',
            apellidos='Test',
            email='usuario@test.com',
            telefono='600000000',
            direccion='Test',
            ciudad='Sevilla',
            codigo_postal='41001',
            password='password123'
        )
    
    def test_login_correcto(self):
        """Test login con credenciales correctas"""
        response = self.client.post(
            reverse('login'),
            {'email': 'usuario@test.com', 'password': 'password123'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect al perfil
        self.assertEqual(self.client.session['cliente_id'], self.cliente.id)
    
    def test_login_incorrecto(self):
        """Test login con contraseña incorrecta"""
        response = self.client.post(
            reverse('login'),
            {'email': 'usuario@test.com', 'password': 'wrongpassword'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'incorrectos')
    
    def test_registro_nuevo_usuario(self):
        """Test registro de nuevo usuario"""
        response = self.client.post(
            reverse('registro'),
            {
                'nombre': 'Nuevo',
                'apellidos': 'Usuario',
                'email': 'nuevo@test.com',
                'telefono': '611111111',
                'direccion': 'Nueva 456',
                'ciudad': 'Madrid',
                'codigo_postal': '28001',
                'password': 'newpass123',
                'password_confirm': 'newpass123'
            }
        )
        # Verificar que se creó el usuario
        self.assertTrue(Cliente.objects.filter(email='nuevo@test.com').exists())
        nuevo_cliente = Cliente.objects.get(email='nuevo@test.com')
        self.assertEqual(nuevo_cliente.nombre, 'Nuevo')
        self.assertEqual(nuevo_cliente.ciudad, 'Madrid')
    
    def test_logout(self):
        """Test cerrar sesión"""
        session = self.client.session
        session['cliente_id'] = self.cliente.id
        session.save()
        
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('cliente_id', self.client.session)

