from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files import File
import requests
import os
import shutil
from pathlib import Path
from home.models import (
    Marca, Categoria, Producto, TallaProducto, ImagenProducto,
    Cliente, Articulo, Escaparate
)


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de ejemplo'

    def descargar_imagen(self, url, nombre_archivo):
        """Descarga una imagen de una URL y devuelve un ContentFile"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, timeout=15, headers=headers, allow_redirects=True)
            if response.status_code == 200:
                return ContentFile(response.content, name=nombre_archivo)
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠ Error HTTP {response.status_code} descargando imagen'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠ Error descargando imagen: {e}'))
        return None

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando seeder...')

        # Limpiar datos existentes
        self.stdout.write('Limpiando datos existentes...')
        TallaProducto.objects.all().delete()
        ImagenProducto.objects.all().delete()
        Producto.objects.all().delete()
        Categoria.objects.all().delete()
        Marca.objects.all().delete()
        Escaparate.objects.all().delete()
        Articulo.objects.all().delete()
        Cliente.objects.all().delete()
        
        # Limpiar completamente el directorio de productos
        media_path = Path('media/productos')
        if media_path.exists():
            shutil.rmtree(media_path)
            self.stdout.write(self.style.SUCCESS('✓ Directorio media/productos limpiado'))
        
        # Recrear el directorio vacío
        media_path.mkdir(parents=True, exist_ok=True)

        # Crear Marcas
        self.stdout.write('Creando marcas...')
        marcas = {
            'EcoGarden': Marca.objects.create(nombre='EcoGarden'),
            'PlantLife': Marca.objects.create(nombre='PlantLife'),
            'GreenWorld': Marca.objects.create(nombre='GreenWorld'),
            'CactusKing': Marca.objects.create(nombre='CactusKing'),
        }
        self.stdout.write(self.style.SUCCESS(f'✓ {len(marcas)} marcas creadas'))

        # Crear Categorías
        self.stdout.write('Creando categorías...')
        categorias = {
            'Cactus': Categoria.objects.create(
                nombre='Cactus',
                descripcion='Plantas cactáceas de diversos tamaños y formas'
            ),
            'Suculentas': Categoria.objects.create(
                nombre='Suculentas',
                descripcion='Plantas suculentas ideales para interiores'
            ),
            'Plantas de Interior': Categoria.objects.create(
                nombre='Plantas de Interior',
                descripcion='Plantas perfectas para decorar tu hogar'
            ),
            'Plantas de Exterior': Categoria.objects.create(
                nombre='Plantas de Exterior',
                descripcion='Plantas resistentes para jardines'
            ),
            'Macetas': Categoria.objects.create(
                nombre='Macetas',
                descripcion='Macetas decorativas de diversos materiales'
            ),
            'Herramientas': Categoria.objects.create(
                nombre='Herramientas',
                descripcion='Herramientas para jardinería'
            ),
        }
        self.stdout.write(self.style.SUCCESS(f'✓ {len(categorias)} categorías creadas'))

        # Crear Productos
        self.stdout.write('Creando productos...')
        
        productos_data = [
            # Cactus
            {
                'nombre': 'Cactus Dorado',
                'descripcion': 'Hermoso cactus dorado, perfecto para espacios pequeños. Requiere poca agua y mucha luz solar.',
                'precio': 12.99,
                'marca': marcas['CactusKing'],
                'categoria': categorias['Cactus'],
                'genero': 'unisex',
                'color': 'Verde/Dorado',
                'material': 'Natural',
                'stock': 25,
                'esta_disponible': True,
                'es_destacado': True,
            },
            {
                'nombre': 'Cactus Mini Colección',
                'descripcion': 'Set de 3 mini cactus variados en macetas decorativas. Ideales para escritorio.',
                'precio': 8.99,
                'marca': marcas['CactusKing'],
                'categoria': categorias['Cactus'],
                'genero': 'unisex',
                'color': 'Verde',
                'material': 'Natural',
                'stock': 40,
                'esta_disponible': True,
                'es_destacado': True,
            },
            {
                'nombre': 'Cactus San Pedro Grande',
                'descripcion': 'Cactus San Pedro de gran tamaño, perfecto para jardines. Muy resistente.',
                'precio': 45.00,
                'marca': marcas['CactusKing'],
                'categoria': categorias['Cactus'],
                'genero': 'unisex',
                'color': 'Verde',
                'material': 'Natural',
                'stock': 8,
                'esta_disponible': True,
                'es_destacado': False,
            },
            
            # Suculentas
            {
                'nombre': 'Set de Suculentas Mix',
                'descripcion': 'Colección de 5 suculentas diferentes. Perfectas para decoración de interiores.',
                'precio': 15.99,
                'marca': marcas['PlantLife'],
                'categoria': categorias['Suculentas'],
                'genero': 'unisex',
                'color': 'Varios',
                'material': 'Natural',
                'stock': 30,
                'esta_disponible': True,
                'es_destacado': True,
            },
            {
                'nombre': 'Echeveria Elegans',
                'descripcion': 'Suculenta de hojas en forma de rosa, muy elegante y fácil de cuidar.',
                'precio': 6.50,
                'marca': marcas['PlantLife'],
                'categoria': categorias['Suculentas'],
                'genero': 'unisex',
                'color': 'Verde claro',
                'material': 'Natural',
                'stock': 50,
                'esta_disponible': True,
                'es_destacado': False,
            },
            
            # Plantas de Interior
            {
                'nombre': 'Monstera Deliciosa',
                'descripcion': 'Planta tropical de grandes hojas perforadas. Perfecta para dar vida a cualquier espacio.',
                'precio': 32.00,
                'marca': marcas['GreenWorld'],
                'categoria': categorias['Plantas de Interior'],
                'genero': 'unisex',
                'color': 'Verde oscuro',
                'material': 'Natural',
                'stock': 15,
                'esta_disponible': True,
                'es_destacado': True,
            },
            {
                'nombre': 'Pothos Dorado',
                'descripcion': 'Planta colgante de fácil cuidado, purifica el aire. Ideal para principiantes.',
                'precio': 18.50,
                'marca': marcas['GreenWorld'],
                'categoria': categorias['Plantas de Interior'],
                'genero': 'unisex',
                'color': 'Verde/Amarillo',
                'material': 'Natural',
                'stock': 35,
                'esta_disponible': True,
                'es_destacado': False,
            },
            {
                'nombre': 'Ficus Lyrata',
                'descripcion': 'Planta serpiente, extremadamente resistente. Perfecta para oficinas.',
                'precio': 22.00,
                'marca': marcas['EcoGarden'],
                'categoria': categorias['Plantas de Interior'],
                'genero': 'unisex',
                'color': 'Verde/Amarillo',
                'material': 'Natural',
                'stock': 20,
                'esta_disponible': True,
                'es_destacado': False,
            },
            
            # Plantas de Exterior
            {
                'nombre': 'Lavanda Aromática',
                'descripcion': 'Aromática lavanda perfecta para jardines. Atrae mariposas y abejas.',
                'precio': 12.00,
                'marca': marcas['EcoGarden'],
                'categoria': categorias['Plantas de Exterior'],
                'genero': 'unisex',
                'color': 'Morado',
                'material': 'Natural',
                'stock': 45,
                'esta_disponible': True,
                'es_destacado': True,
            },
            {
                'nombre': 'Rosal Trepador Rojo',
                'descripcion': 'Rosal compacto con flores rojas. Florece abundantemente en primavera.',
                'precio': 16.50,
                'marca': marcas['EcoGarden'],
                'categoria': categorias['Plantas de Exterior'],
                'genero': 'unisex',
                'color': 'Rojo',
                'material': 'Natural',
                'stock': 25,
                'esta_disponible': True,
                'es_destacado': False,
            },
            
            # Macetas
            {
                'nombre': 'Maceta Terracota 15cm',
                'descripcion': 'Maceta clásica de terracota, ideal para todo tipo de plantas. Diámetro 15cm.',
                'precio': 5.99,
                'marca': None,
                'categoria': categorias['Macetas'],
                'genero': 'unisex',
                'color': 'Terracota',
                'material': 'Arcilla',
                'stock': 100,
                'esta_disponible': True,
                'es_destacado': False,
            },
            {
                'nombre': 'Maceta Cerámica Rosa',
                'descripcion': 'Elegante maceta de cerámica con acabado mate. Incluye plato inferior.',
                'precio': 9.99,
                'marca': None,
                'categoria': categorias['Macetas'],
                'genero': 'unisex',
                'color': 'Rosa',
                'material': 'Cerámica',
                'stock': 60,
                'esta_disponible': True,
                'es_destacado': False,
            },
            {
                'nombre': 'Set 3 Macetas Bambú',
                'descripcion': 'Conjunto de 3 macetas de bambú ecológicas en diferentes tamaños.',
                'precio': 24.99,
                'marca': None,
                'categoria': categorias['Macetas'],
                'genero': 'unisex',
                'color': 'Natural',
                'material': 'Bambú',
                'stock': 30,
                'esta_disponible': True,
                'es_destacado': True,
            },
            
            # Herramientas
            {
                'nombre': 'Kit Herramientas Jardinería',
                'descripcion': 'Set completo con pala, rastrillo y tijeras de podar. Mango ergonómico.',
                'precio': 29.99,
                'marca': None,
                'categoria': categorias['Herramientas'],
                'genero': 'unisex',
                'color': 'Verde/Negro',
                'material': 'Acero inoxidable',
                'stock': 40,
                'esta_disponible': True,
                'es_destacado': False,
            },
            {
                'nombre': 'Regadera Metal Vintage',
                'descripcion': 'Regadera de metal con diseño vintage. Capacidad 2 litros.',
                'precio': 18.00,
                'marca': None,
                'categoria': categorias['Herramientas'],
                'genero': 'unisex',
                'color': 'Verde menta',
                'material': 'Metal',
                'stock': 25,
                'esta_disponible': True,
                'es_destacado': False,
            },
        ]

        productos = []
        for data in productos_data:
            producto = Producto.objects.create(**data)
            productos.append(producto)

        self.stdout.write(self.style.SUCCESS(f'✓ {len(productos)} productos creados'))

        # Crear imágenes para los productos
        self.stdout.write('Creando imágenes de productos...')
        imagenes_count = 0
        
        # Mapeo de productos a nombres de archivo esperados
        imagenes_map = {
            'Cactus Dorado': 'cactus_dorado.jpg',
            'Cactus Mini Colección': 'cactus_mini_colección.jpg',
            'Cactus San Pedro Grande': 'cactus_san_pedro_grande.jpg',
            'Set de Suculentas Mix': 'set_de_suculentas_mix.jpg',
            'Echeveria Elegans': 'echeveria_elegans.jpg',
            'Monstera Deliciosa': 'monstera_deliciosa.jpg',
            'Pothos Dorado': 'pothos_dorado.jpg',
            'Ficus Lyrata': 'ficus_lyrata.jpg',
            'Lavanda Aromática': 'lavanda_aromática.jpg',
            'Rosal Trepador Rojo': 'rosal_trepador_rojo.jpg',
            'Maceta Terracota 15cm': 'maceta_terracota_15cm.jpg',
            'Maceta Cerámica Rosa': 'maceta_cerámica_rosa.jpg',
            'Set 3 Macetas Bambú': 'set_3_macetas_bambú.jpg',
            'Kit Herramientas Jardinería': 'kit_herramientas_jardinería.jpg',
            'Regadera Metal Vintage': 'regadera_metal_vintage.jpg',
        }
        
        # URLs de respaldo si no existe el archivo local
        imagenes_urls = {
            'Cactus Dorado': 'https://upload.wikimedia.org/wikipedia/commons/2/25/Echinocactus_grusonii_%28aka%29.jpg',
            'Cactus Mini Colección': 'https://gardencentershop.com/media/imgs/almacen_articulo/d9eedc8d-4979-416c-89da-952a5e8225bc/51769471-c56a-4023-9173-78d800b9b88f.jpg',
            'Cactus San Pedro Grande': 'https://jardinpostal.com/wp-content/uploads/2020/06/donpedro-jardin-postal-scaled.jpg',
            'Set de Suculentas Mix': 'https://photo.floraccess.com/6emlsat3amne0gdg0t65od3c7bn12jbpqd60nksj_Preview480.jpg',
            'Echeveria Elegans': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRq4DlaeYZ2ldcXotphLlCt1ONhDi3hiWXeEg&s',
            'Monstera Deliciosa': 'https://florastore.com/cdn/shop/files/3512102_Atmosphere_04_SQ_MJ_1800x1800.jpg?v=1751966143',
            'Pothos Dorado': 'https://res.cloudinary.com/fronda/image/upload/f_auto,q_auto,c_fill,g_center,w_528,h_704/productos/fol/10012/10012157_1.jpg?02-01-2024',
            'Ficus Lyrata': 'https://florastore.com/cdn/shop/files/3313211_Atmosphere_01_SQ.jpg?v=1758705122&width=1080',
            'Lavanda Aromática': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT8tZYEGJ20BRS8LVjzQFDB0MFp3QcyVlOKEw&s',
            'Rosal Trepador Rojo': 'https://media.floresfrescasonline.com/product/rosal-trepador-carmen-800x800.jpg?width=1200',
            'Maceta Terracota 15cm': 'https://alfarerianunez.com/wp-content/uploads/2021/07/maceta-24-barro-frente.jpg',
            'Maceta Cerámica Rosa': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSL6TPYtY-iILoNODXf0mRwIska5tAInFEt1w&s',
            'Set 3 Macetas Bambú': 'https://decorshopping.es/136436-large_default/set-3-maceteros-de-bambu-trenzado.jpg',
            'Kit Herramientas Jardinería': 'https://www.abonoscalsilla.com/wp-content/uploads/2020/07/kit-herramientas-jardin-kamikaze.jpg',
            'Regadera Metal Vintage': 'https://m.media-amazon.com/images/I/71aYlURbsWL.jpg',
        }
        
        for producto in productos:
            if producto.nombre in imagenes_urls:
                url = imagenes_urls[producto.nombre]
                filename = imagenes_map[producto.nombre]
                imagen_file = self.descargar_imagen(url, filename)
                
                if imagen_file:
                    ImagenProducto.objects.create(
                        producto=producto,
                        imagen=imagen_file,
                        es_principal=True
                    )
                    imagenes_count += 1
                    self.stdout.write(f'  ✓ Imagen descargada para: {producto.nombre}')
        
        self.stdout.write(self.style.SUCCESS(f'✓ {imagenes_count} imágenes creadas'))


        # Crear tallas para algunos productos (macetas principalmente)
        self.stdout.write('Creando tallas...')
        tallas_count = 0
        
        # Macetas tienen tallas
        for producto in Producto.objects.filter(categoria=categorias['Macetas']):
            TallaProducto.objects.create(producto=producto, talla='S', stock=20)
            TallaProducto.objects.create(producto=producto, talla='M', stock=25)
            TallaProducto.objects.create(producto=producto, talla='L', stock=15)
            tallas_count += 3

        self.stdout.write(self.style.SUCCESS(f'✓ {tallas_count} tallas creadas'))

        # Crear clientes de ejemplo
        self.stdout.write('Creando clientes de ejemplo...')
        clientes_data = [
            {
                'nombre': 'Admin',
                'apellidos': 'TodoJardin',
                'email': 'admin@todojardin.es',
                'telefono': '+34 600 000 000',
                'direccion': 'Calle Admin 1',
                'ciudad': 'Sevilla',
                'codigo_postal': '41001',
                'password': 'admin123',
                'is_admin': True,
            },
            {
                'nombre': 'María',
                'apellidos': 'García López',
                'email': 'maria.garcia@example.com',
                'telefono': '+34 600 111 222',
                'direccion': 'Calle Sevilla 123',
                'ciudad': 'Sevilla',
                'codigo_postal': '41001',
                'password': 'password123',
            },
            {
                'nombre': 'Juan',
                'apellidos': 'Martínez Ruiz',
                'email': 'juan.martinez@example.com',
                'telefono': '+34 600 333 444',
                'direccion': 'Avenida Reina Mercedes 45',
                'ciudad': 'Sevilla',
                'codigo_postal': '41012',
                'password': 'password123',
            },
            {
                'nombre': 'Ana',
                'apellidos': 'Rodríguez Sánchez',
                'email': 'ana.rodriguez@example.com',
                'telefono': '+34 600 555 666',
                'direccion': 'Plaza Nueva 8',
                'ciudad': 'Sevilla',
                'codigo_postal': '41003',
                'password': 'password123',
            },
            {
                'nombre': 'Carlos',
                'apellidos': 'Fernández Gil',
                'email': 'carlos.fernandez@example.com',
                'telefono': '+34 611 222 333',
                'direccion': 'Calle Betis 21',
                'ciudad': 'Sevilla',
                'codigo_postal': '41010',
                'password': 'password123',
            },
            {
                'nombre': 'Laura',
                'apellidos': 'Jiménez Moreno',
                'email': 'laura.jimenez@example.com',
                'telefono': '+34 622 333 444',
                'direccion': 'Avenida de la Constitución 15',
                'ciudad': 'Sevilla',
                'codigo_postal': '41004',
                'password': 'password123',
            },
            {
                'nombre': 'Pedro',
                'apellidos': 'Sánchez Vega',
                'email': 'pedro.sanchez@example.com',
                'telefono': '+34 633 444 555',
                'direccion': 'Calle Feria 67',
                'ciudad': 'Sevilla',
                'codigo_postal': '41002',
                'password': 'password123',
            },
            {
                'nombre': 'Carmen',
                'apellidos': 'López Díaz',
                'email': 'carmen.lopez@example.com',
                'telefono': '+34 644 555 666',
                'direccion': 'Plaza de España 3',
                'ciudad': 'Sevilla',
                'codigo_postal': '41013',
                'password': 'password123',
            },
            {
                'nombre': 'Miguel',
                'apellidos': 'Ruiz Blanco',
                'email': 'miguel.ruiz@example.com',
                'telefono': '+34 655 666 777',
                'direccion': 'Calle Sierpes 89',
                'ciudad': 'Sevilla',
                'codigo_postal': '41004',
                'password': 'password123',
            },
            {
                'nombre': 'Elena',
                'apellidos': 'Torres Castro',
                'email': 'elena.torres@example.com',
                'telefono': '+34 666 777 888',
                'direccion': 'Avenida Kansas City 12',
                'ciudad': 'Sevilla',
                'codigo_postal': '41007',
                'password': 'password123',
            },
            {
                'nombre': 'David',
                'apellidos': 'Navarro Prieto',
                'email': 'david.navarro@example.com',
                'telefono': '+34 677 888 999',
                'direccion': 'Calle San Jacinto 34',
                'ciudad': 'Sevilla',
                'codigo_postal': '41010',
                'password': 'password123',
            },
            {
                'nombre': 'Sofía',
                'apellidos': 'Morales Ortiz',
                'email': 'sofia.morales@example.com',
                'telefono': '+34 688 999 000',
                'direccion': 'Plaza del Duque 5',
                'ciudad': 'Sevilla',
                'codigo_postal': '41002',
                'password': 'password123',
            },
        ]

        for data in clientes_data:
            Cliente.objects.create(**data)

        self.stdout.write(self.style.SUCCESS(f'✓ {len(clientes_data)} clientes creados'))

        # Crear pedidos de prueba
        self.stdout.write('Creando pedidos de prueba...')
        from home.models import Pedido, ItemPedido
        from decimal import Decimal
        from datetime import timedelta
        from django.utils import timezone
        import random

        # Obtener clientes y productos
        clientes_list = list(Cliente.objects.filter(is_admin=False))
        productos_list = list(Producto.objects.all())
        
        estados = ['pendiente', 'confirmado', 'procesando', 'enviado', 'entregado', 'cancelado']
        metodos_pago = ['tarjeta', 'contra_reembolso']
        
        pedidos_creados = 0
        
        # Crear 30 pedidos con datos aleatorios
        for i in range(30):
            cliente = random.choice(clientes_list)
            
            # Fecha aleatoria en los últimos 60 días (timezone-aware)
            dias_atras = random.randint(0, 60)
            fecha = timezone.now() - timedelta(days=dias_atras)
            
            # Seleccionar 1-5 productos aleatorios
            num_productos = random.randint(1, 5)
            productos_pedido = random.sample(productos_list, min(num_productos, len(productos_list)))
            
            # Calcular subtotal
            subtotal = Decimal('0.00')
            items_data = []
            
            for producto in productos_pedido:
                cantidad = random.randint(1, 3)
                precio = producto.precio
                item_total = precio * cantidad
                items_data.append({
                    'producto': producto,
                    'cantidad': cantidad,
                    'precio_unitario': precio,
                    'total': item_total
                })
                subtotal += item_total
            
            # Calcular totales
            coste_entrega = Decimal('5.99')
            impuestos = subtotal * Decimal('0.21')
            descuento = Decimal('0.00')
            total = subtotal + coste_entrega + impuestos - descuento
            
            # Crear pedido
            pedido = Pedido.objects.create(
                cliente=cliente,
                subtotal=subtotal,
                coste_entrega=coste_entrega,
                impuestos=impuestos,
                descuento=descuento,
                total=total,
                direccion_envio=cliente.direccion,
                telefono=cliente.telefono,
                metodo_pago=random.choice(metodos_pago),
                estado=random.choice(estados),
                numero_pedido=f'PED-{10000 + i}'
            )
            
            # Actualizar fecha de creación manualmente con timezone
            Pedido.objects.filter(id=pedido.id).update(fecha_creacion=fecha)
            
            # Crear items del pedido
            for item_data in items_data:
                ItemPedido.objects.create(
                    pedido=pedido,
                    producto=item_data['producto'],
                    cantidad=item_data['cantidad'],
                    precio_unitario=item_data['precio_unitario'],
                    total=item_data['total']
                )
            
            pedidos_creados += 1
        
        self.stdout.write(self.style.SUCCESS(f'✓ {pedidos_creados} pedidos creados'))

        # Crear artículos para el escaparate
        self.stdout.write('Creando artículos de escaparate...')
        articulo1 = Articulo.objects.create(
            nombre='Promoción Primavera',
            descripcion='¡25% de descuento en todas las plantas de interior!'
        )
        Escaparate.objects.create(articulo=articulo1)
        self.stdout.write(self.style.SUCCESS('✓ Escaparate creado'))

        self.stdout.write(self.style.SUCCESS('\n¡Seeder completado exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'''
Resumen:
- {len(marcas)} marcas
- {len(categorias)} categorías
- {len(productos)} productos
- {tallas_count} tallas
- {len(clientes_data)} clientes
- {pedidos_creados} pedidos
- 1 escaparate

Credenciales de prueba:
Admin: admin@todojardin.es / admin123
Usuario: maria.garcia@example.com / password123
        '''))
