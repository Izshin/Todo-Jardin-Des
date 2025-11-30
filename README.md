# Todo Jardin - Tienda Virtual WEB: https://jhonpgpi.eu.pythonanywhere.com/

Proyecto de tienda online de jardinería desarrollado en Django.

## Setup Inicial

### 1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd Todo-Jardin
```

### 2. Crear y activar entorno virtual
```bash
python -m venv venv
venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 3. Instalar dependencias
```bash
pip install django pillow braintree
```

### 4. Configurar base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Cargar datos de prueba
```bash
python manage.py seed
```

### 6. Ejecutar servidor
```bash
python manage.py runserver
```

Accede a `http://127.0.0.1:8000/`

## Usuarios de Prueba

### Usuarios Clientes
- **Email:** maria.garcia@example.com  
  **Contraseña:** password123

- **Email:** juan.martinez@example.com  
  **Contraseña:** password123

- **Email:** ana.lopez@example.com  
  **Contraseña:** password123

### Usuario Administrador
- **Email:** admin@todojardin.com  
  **Contraseña:** admin123
  **Panel:** `/admin-panel/`

## Funcionalidades Principales

### Sistema de Usuarios
- ✅ **Registro y autenticación completa**
  - Registro con validación de email único
  - Login/logout con sesiones
  - Perfil editable (datos personales, contraseña)
  - **Preferencia de método de pago** - Guardar tarjeta o contra reembolso como favorito
  - Eliminar cuenta con confirmación
  - Separación completa: clientes no acceden a admin, admins no acceden a cliente

### Catálogo y Productos
- ✅ **Sistema de productos completo**
  - Productos con imágenes, descripciones, precios, stock
  - Categorías y marcas organizadas
  - Productos destacados en homepage
  - Sistema de imágenes múltiples por producto
  - Productos relacionados en detalle
  
- ✅ **Búsqueda y filtrado avanzado**
  - Barra de búsqueda global en todas las páginas
  - Búsqueda por nombre y descripción
  - Filtros por categorías (múltiples)
  - Filtros por marcas (múltiples)
  - **Slider dual de rango de precio** con tema verde corporativo
  - Filtro de productos destacados
  - Ordenamiento por nombre y precio
  - Badges visuales de filtros activos

### Sistema de Compras
- ✅ **Carrito de compras inteligente**
  - Mini-carrito desplegable en navegación
  - Añadir/eliminar productos
  - Actualizar cantidades
  - Cálculo automático de totales
  - Persistencia entre sesiones
  
- ✅ **Checkout tradicional en 3 pasos**
  - **Paso 1:** Datos de envío y tipo de entrega (domicilio/tienda)
  - **Paso 2:** Método de pago (tarjeta/contra reembolso)
  - **Paso 3:** Confirmación con resumen completo
  - Navegación con indicadores de progreso
  - Datos persistidos en sesión entre pasos
  
- ✅ **⚡ Compra Rápida (1-Click)**
  - Botón destacado en listado de productos
  - Todo en una sola página (sin pasos)
  - Selector de cantidad con botones +/-
  - Cálculos en tiempo real (subtotal, IVA, envío, total)
  - Pedidos creados directamente como "confirmados"
  - Ideal para compras rápidas de un solo producto

- ✅ **Compra sin registro**
  - Checkout completo como invitado
  - Creación automática de cuenta temporal
  - Banner sugerencia para crear cuenta
  - Sistema de confirmación por email

### Métodos de Pago
- ✅ **💳 Integración Braintree**
  - Drop-in UI seguro para tarjetas
  - Tokenización de datos sensibles
  - Sandbox para pruebas
  - Procesamiento real de transacciones
  - **Tarjetas de prueba:**
    - Visa: 4111 1111 1111 1111
    - Mastercard: 5555 5555 5555 4444
    - CVV: cualquier 3 dígitos
    - Fecha: cualquier fecha futura

- ✅ **💰 Pago Contra Reembolso**
  - Pago en efectivo al recibir
  - Sin requerimiento de tarjeta
  - Estado especial "En espera de pago"
  - Banner informativo diferenciado
  - **Preferencia guardable** en perfil de usuario

- ✅ **Método de pago favorito**
  - Campo en registro y perfil
  - Auto-selección en checkout normal y rápido
  - Interfaz Braintree se oculta si favorito es reembolso
  - Mejora la experiencia en compras recurrentes

### Gestión de Pedidos
- ✅ **Historial de pedidos** (usuarios registrados)
  - Lista completa ordenada por fecha
  - Estados visuales con badges de color
  - Detalles completos de cada pedido
  - Resumen financiero
  - Información de envío y pago
  
- ✅ **Rastreador público de pedidos**
  - Búsqueda sin necesidad de cuenta
  - Acceso desde homepage
  - Formatos flexibles (PED-XXXXXX, #PED-XXXXXX, XXXXXX)
  - Diseño verde corporativo
  - Información completa del pedido

- ✅ **Estados de pedido**
  - 🟡 Pendiente
  - 🟠 En espera de pago (contra reembolso)
  - 🔵 Confirmado
  - 🟣 Procesando
  - 🟪 Enviado
  - 🟢 Entregado
  - 🔴 Cancelado

### Comunicaciones
- ✅ **Sistema de emails UTF-8**
  - Soporte completo para español (ñ, á, é, etc.)
  - Confirmaciones de pedido
  - Emails informativos diferenciados por tipo de pago
  - Plantillas HTML con diseño corporativo

## Panel de Administración

Sistema completo de gestión con tema azul corporativo:

### Acceso y Seguridad
- **Ruta:** `/admin-panel/`
- **Requiere:** Usuario con `is_admin = True`
- **Separación estricta:** Admins no pueden acceder a vistas de cliente
- **Auto-redirección:** Intentos de acceso a cliente redirigen a panel admin

### Dashboard Principal
- 📊 Estadísticas generales
  - Total de pedidos
  - Total de productos  
  - Total de usuarios
- 🔗 Accesos rápidos a cada sección
- 🎨 Logo personalizado (LogoAdmin.png)
- 🖼️ Navegación con dropdown mejorado

### Gestión de Pedidos
- 📋 Lista completa con información detallada
- 🏷️ Badges de estado con colores específicos
- 🔄 Cambio de estado con dropdown
- 🔍 Búsqueda por número de pedido (con soporte de #)
- 🗑️ Eliminación con confirmación
- 📦 Información visible:
  - Número de pedido
  - Cliente
  - Fecha
  - Total
  - Estado actual
  - Método de pago

### Gestión de Productos
- 📝 CRUD completo
- 🔍 **Filtrado avanzado:**
  - Búsqueda por nombre/descripción (barra expandida)
  - Multi-select de categorías (scrollbar azul)
  - Multi-select de marcas (scrollbar azul)
  - **Slider dual de rango de precio**:
    - Thumbs de 22px con gradiente azul
    - Barra de progreso visual
    - Labels dinámicos €min y €max
    - Intercambio automático de valores
    - Cálculo desde base de datos
  - Botones Filtrar (azul) y Limpiar (rojo)
- ➕ **Crear/Editar producto:**
  - Todos los campos (precio único simplificado)
  - Vista previa de imagen
  - Creación inline de categorías/marcas
  - Checkbox "Es destacado"
- 🗑️ Eliminación con confirmación

### Gestión de Usuarios
- 👥 Lista completa de usuarios
- ➕ Crear nuevos usuarios
- ✏️ Editar usuarios (incluso el propio)
- 🗑️ Eliminar con protección anti-auto-eliminación
- 👑 Toggle de permisos de administrador
- 📊 Información visible:
  - ID, Email, Nombre completo
  - Estado de administrador
  - Fecha de creación

### Configuración del Sistema
- ⚙️ **Configuración de envío**
  - Coste de envío estándar editable
  - Monto mínimo para envío gratis
  - Formulario con validación
  - Accesible desde dropdown en todas las páginas admin

### Diseño y UX
- 🎨 **Paleta azul corporativa**
  - Azul principal: #60A5FA → #3B82F6
  - Amarillo (volver): #FCD34D → #F59E0B
  - Rojo (eliminar): #F87171 → #DC2626
- 🖱️ **Efectos interactivos:**
  - Transform translateY en hover
  - Box-shadows con opacidad
  - Transiciones suaves (0.2s)
- 📱 Responsive
- ✨ Confirmaciones JavaScript

## Mejoras Técnicas Recientes

### Eliminación de Campo "Género"
- ❌ Removido campo inapropiado `genero` de productos
- ✅ Migración 0009 aplicada
- ✅ Seed.py actualizado (15 líneas eliminadas)
- ✅ Templates actualizados
### Preferencia de Método de Pago
- ✅ Campo `metodo_pago_favorito` en modelo Cliente
- ✅ Migración 0010 aplicada
- ✅ Selector en registro y perfil de usuario
- ✅ Auto-selección en checkout normal y rápido
- ✅ Interfaz adaptativa (Braintree se oculta si favorito es reembolso)
- ✅ Estilos CSS consistentes con la aplicación

### Gestión de Envíos Dinámica
- ⚙️ Modelo `ConfiguracionEnvio` (singleton)
- 💰 Coste de envío estándar configurable
- 🎁 Monto mínimo para envío gratis configurable
- 👨‍💼 Panel admin para editar configuración
- 🔗 Enlace en todas las topbars de admin
- 📦 Cálculo dinámico en checkout

### Mejoras de UI/UX
- 🎨 CSS mejorado para selectores de método de pago
- 🚫 Emojis eliminados de checkout rápido (diseño limpio)
- 🎯 Bloqueo total de acceso de admins a vistas de cliente
- ↩️ Auto-redirección a panel admin al intentar acceder a cliente
- 🔍 Búsqueda de pedidos con soporte de prefijo #
- 🎨 Banners de invitado con tema azul
- 📱 Responsive en todos los formularios

## Estructura del Proyecto

```
Todo-Jardin/
├── home/                          # App principal
│   ├── models.py                 # Modelos de BD (Cliente, Producto, Pedido, etc.)
│   ├── views.py                  # Vistas de cliente
│   ├── views_admin.py            # Vistas de administración
│   ├── templates/                # HTML templates
│   │   ├── mainPage.html        # Página principal
│   │   ├── productos.html       # Catálogo
│   │   ├── carrito.html         # Carrito
│   │   ├── checkout*.html       # Proceso de compra
│   │   ├── perfil.html          # Perfil de usuario
│   │   ├── admin_*.html         # Páginas del panel admin
│   │   └── ...
│   ├── static/                   # Recursos estáticos
│   │   ├── styles/
│   │   │   ├── main.css         # Estilos globales (tema verde)
│   │   │   ├── admin.css        # Estilos del panel (tema azul)
│   │   │   ├── carrito.css
│   │   │   ├── checkout.css
│   │   │   ├── perfil.css
│   │   │   └── ...
│   │   └── images/
│   │       ├── Logo.png         # Logo cliente
│   │       └── LogoAdmin.png    # Logo admin
│   ├── migrations/               # Migraciones de BD
│   │   ├── 0009_remove_producto_genero.py
│   │   ├── 0010_cliente_metodo_pago_favorito.py
│   │   └── ...
│   └── management/
│       └── commands/
│           └── seed.py          # Comando para datos de prueba
├── tienda_virtual/               # Configuración Django
│   ├── settings.py              # Configuración del proyecto
│   └── urls.py                  # Rutas principales
├── media/                        # Archivos subidos (imágenes)
│   └── productos/
├── db.sqlite3                    # Base de datos SQLite
├── manage.py                     # CLI de Django
└── README.md                     # Este archivo
```

## Comandos Útiles

```bash
# Crear migraciones después de cambios en models.py
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Recargar datos de prueba (borra datos existentes)
python manage.py seed

# Ejecutar servidor de desarrollo
python manage.py runserver

# Ejecutar tests
python manage.py test home

# Ejecutar tests con verbosidad
python manage.py test home --verbosity=2
```

## Rutas Principales

### Rutas de Cliente
- `/` - Página principal con productos destacados
- `/productos/` - Catálogo completo con filtros avanzados
- `/producto/<id>/` - Detalle de producto con relacionados
- `/carrito/` - Ver y gestionar carrito
- `/checkout/` - Paso 1: Información de envío
- `/checkout/paso2/` - Paso 2: Método de pago
- `/checkout/paso3/` - Paso 3: Confirmación
- `/checkout-rapido/<id>/` - Compra rápida de 1 click
- `/procesar-checkout-rapido/` - Procesamiento de compra rápida
- `/procesar-pago/` - Procesamiento de pago (Braintree/reembolso)
- `/confirmacion/<id>/` - Confirmación del pedido
- `/confirmar-pedido/<id>/` - Confirmación por email (con token)
- `/mis-pedidos/` - Historial de pedidos (autenticado)
- `/buscar-pedido/` - Rastreador público de pedidos
- `/login/` - Iniciar sesión
- `/registro/` - Crear cuenta
- `/perfil/` - Perfil de usuario
- `/logout/` - Cerrar sesión
- `/terminos/` - Términos y condiciones

### Rutas de Administración
- `/admin-panel/` - Dashboard principal
- `/admin-perfil/` - Perfil de administrador
- `/admin-panel/pedidos/` - Gestión de pedidos
- `/admin-panel/pedidos/<id>/estado/` - Actualizar estado
- `/admin-panel/pedidos/<id>/eliminar/` - Eliminar pedido
- `/admin-panel/productos/` - Gestión de productos
- `/admin-panel/productos/crear/` - Crear producto
- `/admin-panel/productos/<id>/editar/` - Editar producto
- `/admin-panel/productos/<id>/eliminar/` - Eliminar producto
- `/admin-panel/usuarios/` - Gestión de usuarios
- `/admin-panel/usuarios/crear/` - Crear usuario
- `/admin-panel/usuarios/<id>/editar/` - Editar usuario
- `/admin-panel/usuarios/<id>/toggle-admin/` - Cambiar permisos admin
- `/admin-panel/usuarios/<id>/eliminar/` - Eliminar usuario
- `/admin-panel/configuracion-envio/` - Configurar envíos

## Tecnologías y Dependencias

### Backend
- **Django 5.2** - Framework web principal
- **Python 3.x** - Lenguaje de programación
- **SQLite** - Base de datos (desarrollo)
- **Pillow** - Procesamiento de imágenes
- **Braintree SDK 4.40.0** - Integración de pagos

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos con gradientes y animaciones
- **JavaScript Vanilla** - Interactividad sin dependencias
- **Braintree Drop-in UI** - Widget de pago

### Características de Seguridad
- 🔐 CSRF protection en todos los formularios
- 🔒 Tokenización de tarjetas (Braintree)
- 🛡️ Validación de permisos en vistas admin
- 👤 Separación estricta cliente/admin
- 📧 Confirmación de pedidos por email
- 🔑 Sesiones Django para autenticación

## Testing

Suite completa de 19 tests unitarios:

### Categorías de Tests
- **Modelos** - Creación y representación de objetos
- **Vistas** - Carga correcta de páginas
- **Carrito** - Operaciones de añadir/ver productos
- **Búsqueda** - Rastreador de pedidos
- **Autenticación** - Login, registro, logout

### Ejecutar Tests
```bash
# Todos los tests
python manage.py test home

# Con detalle
python manage.py test home --verbosity=2

# Tests específicos
python manage.py test home.tests.ClienteModelTests
python manage.py test home.tests.BuscarPedidoTests
```

### Resultados
```
Ran 19 tests in 0.172s
OK
```

## Configuración de Braintree

### Credenciales Sandbox
```python
BRAINTREE_MERCHANT_ID = 'szwzx5mdn5g7p9sg'
BRAINTREE_PUBLIC_KEY = 'mwxwdwf76j6b5vsh'
BRAINTREE_PRIVATE_KEY = '11c034c8c8e0eb562a7809dcb0cb1593'
BRAINTREE_ENVIRONMENT = 'Sandbox'
```

### Tarjetas de Prueba
| Tarjeta | Número | CVV | Fecha |
|---------|--------|-----|-------|
| Visa | 4111 1111 1111 1111 | Cualquier 3 dígitos | Cualquier fecha futura |
| Mastercard | 5555 5555 5555 4444 | Cualquier 3 dígitos | Cualquier fecha futura |

## Notas de Desarrollo

### Sistema de Sesiones
- Datos de checkout persisten entre pasos
- Método de pago almacenado en sesión
- Payment nonce de Braintree en sesión temporal
- Limpieza automática después de completar pedido

### Estados de Pedido y Flujo
- **Checkout normal (3 pasos):**
  - Inicial: `pendiente`
  - Después de email: `confirmado`
  - Con tarjeta: transacción procesada
  - Con reembolso: `en_espera_pago`

- **Checkout rápido (1 paso):**
  - Inicial: `confirmado` (directo)
  - Stock reducido inmediatamente
  - No requiere confirmación por email

### Método de Pago Favorito
- Guardado en campo `Cliente.metodo_pago_favorito`
- Opciones: `tarjeta` o `reembolso`
- Auto-selección en checkout paso 2 y checkout rápido
- Interfaz Braintree se muestra/oculta según preferencia
- Mejora UX al evitar selección manual en cada compra

### Gestión de Imágenes
- Directorio `media/productos/` limpiado en cada seed
- Prevención de duplicados con sufijos auto-generados
- Descarga fresca desde URLs en cada seed
- Vista previa con FileReader API en admin

### Sistema de Emails
- `EmailMultiAlternatives` con UTF-8 explícito
- Soporte completo para caracteres españoles
- Plantillas HTML con diseño corporativo
- Headers Content-Type configurados
- Diferenciación por tipo de pago

### Seguridad y Permisos
- Función `bloquear_acceso_admin()` en todas las vistas de cliente
- Función `es_usuario_admin()` para verificación
- Auto-redirección de admins a panel
- Protección contra auto-eliminación de usuarios
- Validación de email único en registro/edición

## Mejoras Futuras Sugeridas

- [ ] Implementar PostgreSQL para producción
- [ ] Sistema de reseñas y calificaciones
- [ ] Wishlist de productos
- [ ] Cupones y descuentos
- [ ] Notificaciones por email de cambios de estado
- [ ] Sistema de devoluciones
- [ ] Integración con API de envíos
- [ ] Dashboard de analytics para admin
- [ ] Exportación de reportes (PDF/Excel)
- [ ] Multi-idioma (i18n)
- [ ] PWA con funcionalidad offline
- [ ] Recuperación de contraseña
- [ ] Verificación de email en registro

## Soporte y Contacto

- **Email:** todojardin@example.com
- **Teléfono:** +34 123 456 789
- **Dirección:** Calle Ejemplo 123, 41001 Sevilla, España

## Licencia

Este proyecto es software educativo desarrollado para fines académicos.

---

**Última actualización:** Noviembre 2025  
**Versión:** 2.0  
**Desarrolladores:** Equipo Todo Jardin

## Integración de Braintree (PB-14)

Sistema de pago seguro mediante Braintree:

### Configuración (Sandbox)
```python
BRAINTREE_MERCHANT_ID = 'szwzx5mdn5g7p9sg'
BRAINTREE_PUBLIC_KEY = 'mwxwdwf76j6b5vsh'
BRAINTREE_PRIVATE_KEY = '11c034c8c8e0eb562a7809dcb0cb1593'
BRAINTREE_ENVIRONMENT = 'Sandbox'
```

### Tarjetas de Prueba
- **Visa:** 4111 1111 1111 1111
- **Mastercard:** 5555 5555 5555 4444
- **Fecha:** Cualquier fecha futura
- **CVV:** Cualquier 3 dígitos

### Características de Seguridad
- ✅ Drop-in UI de Braintree (iframe seguro)
- ✅ Datos de tarjeta nunca tocan el servidor
- ✅ Tokenización automática (payment_method_nonce)
- ✅ Cifrado TLS/HTTPS
- ✅ Cumplimiento PCI-DSS sin certificación
- ✅ Transacciones reales en sandbox
- ✅ Manejo de errores de pago

## Pago Contra Reembolso (PB-24)

Sistema dual de métodos de pago:

### Métodos Disponibles
- 💳 **Tarjeta de Crédito/Débito** - Pago inmediato vía Braintree
- 💰 **Contra Reembolso** - Pago en efectivo al recibir el pedido

### Funcionamiento
1. **Paso 2 del Checkout** - Selector visual de método de pago
2. **Tarjeta seleccionada** - Se muestra interfaz Braintree Drop-in
3. **Reembolso seleccionado** - Se oculta interfaz de tarjeta, banner informativo
4. **Procesamiento condicional** - Backend procesa según método elegido
5. **Confirmación diferenciada** - Banner naranja para pedidos contra reembolso

### Características
- ✅ Selector de método con tarjetas visuales hover
- ✅ JavaScript condicional (Braintree solo para tarjeta)
- ✅ Persistencia de método en sesión
- ✅ Validación backend del método elegido
- ✅ Estados de pedido apropiados por método
- ✅ Banners informativos en confirmación

## Historial de Pedidos

Los usuarios registrados pueden ver su historial completo:

- 📋 Lista de todos los pedidos ordenados por fecha
- 🏷️ Estados visuales con badges de color:
  - 🟡 Pendiente
  - 🟢 Confirmado
  - 🔵 Procesando
  - 🟣 Enviado
  - 🟢 Entregado
  - 🔴 Cancelado
- 📦 Detalles de productos con imágenes
- 💰 Resumen financiero completo
- 📍 Dirección de envío
- 💳 Método de pago utilizado
- 🔍 Botón "Ver Detalles" para cada pedido

Acceso: Desde perfil → "Mis Pedidos" o directamente en `/mis-pedidos/`

## Estructura del Proyecto

```
PGPI-G2.10/
├── home/                  # App principal
│   ├── models.py         # Modelos de BD
│   ├── views.py          # Lógica de vistas
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, imágenes
├── tienda_virtual/       # Configuración Django
├── manage.py
└── db.sqlite3            # Base de datos (no trackear en git)
```

## Comandos Útiles

```bash
# Crear migraciones después de cambios en models.py
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Recargar datos de prueba (borra datos existentes)
python manage.py seed
```

## Rutas Principales

- `/` - Página principal con productos destacados
- `/productos/` - Catálogo completo con filtros
- `/producto/<id>/` - Detalle de producto
- `/carrito/` - Ver carrito de compras
- `/checkout/` - Paso 1: Información de envío y tipo de entrega
- `/checkout/paso2/` - Paso 2: Selector de método de pago
- `/checkout/paso3/` - Paso 3: Confirmación
- `/procesar-pago/` - Procesamiento de pago (Braintree o reembolso)
- `/checkout-rapido/<id>/` - **Compra rápida de 1 click** (sin carrito)
- `/procesar-checkout-rapido/` - Procesamiento de compra rápida
- `/confirmacion/<id>/` - Confirmación del pedido
- `/mis-pedidos/` - Historial de pedidos (usuarios registrados)
- `/buscar-pedido/` - **Rastreador de pedidos público** (sin registro requerido)
- `/terminos/` - Términos y Condiciones
- `/login/` - Iniciar sesión
- `/registro/` - Crear cuenta nueva
- `/perfil/` - Perfil del usuario

## Rastreador de Pedidos (Nuevo)

Sistema de búsqueda de pedidos para usuarios no registrados:

### Características
- 🔍 **Búsqueda por número de pedido** - Sin necesidad de cuenta
- 📱 **Acceso desde página principal** - Botón destacado en hero section
- 🎨 **Diseño consistente** - Paleta verde corporativa (#6ba83e → #5a9032)
- 🔐 **Formatos flexibles** - Acepta PED-XXXXXX, #PED-XXXXXX o solo XXXXXX
- 📊 **Información completa**:
  - Estado del pedido con badges de color
  - Lista de productos con imágenes
  - Fecha de creación
  - Total del pedido
  - Dirección de envío (si aplica)

### Uso
1. Acceder desde `/buscar-pedido/` o botón en homepage
2. Ingresar número de pedido (ej: PED-27DFAA12)
3. Ver información completa del pedido

### UX Mejorada
- Footer siempre visible en la parte inferior
- Botón "Volver al Inicio" con estilo verde corporativo
- Formulario con fondo degradado verde suave
- Mensajes de error claros para pedidos no encontrados
- Contenedor del pedido con efecto hover elevado

## Testing

Suite completa de tests unitarios implementada con Django TestCase:

### Cobertura de Tests (19 total)

#### Tests de Modelos
- ✅ Creación de clientes
- ✅ Representación string de clientes
- ✅ Creación de productos

#### Tests de Vistas
- ✅ Página principal carga correctamente
- ✅ Página de productos muestra catálogo
- ✅ Detalle de producto funciona
- ✅ Páginas de login y registro cargan

#### Tests de Carrito
- ✅ Ver carrito sin items
- ✅ Agregar productos al carrito
- ✅ Cantidad correcta al agregar múltiples veces

#### Tests de Búsqueda de Pedidos
- ✅ Página de búsqueda carga correctamente
- ✅ Buscar pedido existente funciona
- ✅ Buscar sin prefijo PED- funciona
- ✅ Mensaje de error para pedidos inexistentes

#### Tests de Autenticación
- ✅ Login con credenciales correctas
- ✅ Login con credenciales incorrectas muestra error
- ✅ Registro de nuevo usuario
- ✅ Logout limpia sesión correctamente

### Ejecutar Tests
```bash
# Ejecutar todos los tests
python manage.py test home

# Con verbosidad alta
python manage.py test home --verbosity=2

# Tests específicos
python manage.py test home.tests.ClienteModelTests
python manage.py test home.tests.BuscarPedidoTests
```

### Resultados
```
Ran 18 tests in 0.172s
OK
```

## Filtrado de Productos

Sistema completo de filtrado tanto para usuarios como para administradores:

### Filtros de Usuario (`/productos/`)
- 🔍 **Búsqueda por texto** - Nombre o descripción de productos
- 🏷️ **Categorías** - Checkboxes para filtrar por categoría
- 🏢 **Marcas** - Checkboxes para filtrar por marca
- 💰 **Rango de precio con slider dual** (tema verde):
  - Slider interactivo de 28px thumbs con gradiente verde
  - Track de 10px con barra visual de progreso verde
  - Labels con fondo verde claro mostrando precio min/max
  - Botón "Aplicar" para ejecutar el filtro
  - Intercambio automático de valores si min > max
  - Rango calculado dinámicamente desde la BD
- 🌟 **Productos destacados** - Checkbox para ver solo destacados
- 📊 **Ordenamiento** - Por nombre, precio ascendente/descendente
- 🎯 **Filtros activos** - Badges visuales mostrando filtros aplicados

### Filtros de Administrador (`/admin-panel/productos/`)
- 🔎 **Búsqueda expandida** - Input más ancho (flex: 2) para nombre/descripción
- 📦 **Multi-select categorías** - Con scrollbar azul personalizado (gradiente #3B82F6→#2563EB)
- 🏭 **Multi-select marcas** - Con scrollbar azul personalizado idéntico
- 💵 **Slider de precio azul** (tema admin):
  - Dual-range slider de 22px thumbs con gradiente azul (#3B82F6→#2563EB)
  - Track de 10px con barra visual azul
  - Labels dinámicos €min y €max actualizados en tiempo real
  - Sin botón aplicar (filtro automático al cambiar)
  - Layout en 3 filas: búsqueda/filtros → slider → botones
  - Max-width 600px para slider (alineado con búsqueda)
- 🎨 **Botones de acción**:
  - "Filtrar" (azul) - Aplicar filtros seleccionados
  - "Limpiar" (rojo) - Resetear todos los filtros
- 📊 **Estado persistente** - Filtros mantienen valores en URL (GET params)

### Características Técnicas
- ✅ **Backend eficiente** - Queries con Q objects y agregaciones (Min/Max)
- ✅ **JavaScript vanilla** - Sin dependencias externas
- ✅ **Cálculo dinámico** - Rango de precios calculado desde BD en cada carga
- ✅ **UX optimizada** - Intercambio automático de valores, sin bloqueos de interacción
- ✅ **Z-index correcto** - Thumbs con z-index: 10, barra visual con pointer-events: none
- ✅ **Responsive** - Adaptación a diferentes tamaños de pantalla
- ✅ **Scrollbars personalizados** - 8px de ancho, tema corporativo (verde/azul)

## Tecnologías Utilizadas

- **Backend:** Django 5.2
- **Base de datos:** SQLite
- **Pasarela de pago:** Braintree SDK 4.40.0
- **Frontend:** HTML5, CSS3, JavaScript vanilla
- **Gestión de imágenes:** Pillow
- **Email:** Django EmailMultiAlternatives con UTF-8

## Notas de Desarrollo

### Checkout en 3 Pasos
- Datos persisten en sesión Django entre pasos
- Validación en cada paso antes de continuar
- Botones de navegación "Volver" en pasos 2 y 3
- Indicadores visuales de progreso completados
- Método de pago almacenado en sesión

### Braintree Integration
- Client token generado por sesión en paso 2
- Payment nonce capturado por JavaScript en Drop-in UI
- Nonce almacenado en sesión y usado en procesamiento final
- Limpieza de sesión después de completar pedido
- Manejo de errores con redirección y mensajes
- Interfaz condicional según método de pago elegido

### Pago Contra Reembolso
- Método de pago persiste en sesión (`metodo_pago`)
- JavaScript oculta/muestra Braintree según selección
- Backend procesa condicionalmente según método
- Sin transaction_id para pedidos contra reembolso
- Banner visual diferenciado en confirmación

### Sistema de Emails
- EmailMultiAlternatives con encoding UTF-8 explícito
- Soporte completo para caracteres españoles (ñ, á, é, í, ó, ú, ü)
- Headers Content-Type configurados correctamente
- Emails HTML con plantillas Django
- Confirmaciones enviadas en creación y confirmación de pedido

### Seeder de Datos
- Elimina y recrea directorio `media/productos/` en cada ejecución
- Previene duplicación de imágenes con sufijos auto-generados
- Descarga imágenes frescas desde URLs en cada seed
- Limpieza completa de datos antes de regenerar

### Estados de Pedido
- `pendiente` - Pedido creado, pago confirmado
- `confirmado` - Pedido verificado y aceptado
- `procesando` - En preparación
- `enviado` - En tránsito
- `entregado` - Completado
- `cancelado` - Cancelado por usuario o fallo

## Panel de Administración

Sistema completo de administración con tema azul consistente:

### Acceso
- Ruta: `/admin-panel/`
- Requiere usuario con permisos de administrador (`is_admin = True`)

### Características Generales
- 🎨 **Diseño consistente** - Tema azul (#60A5FA → #3B82F6) en toda la interfaz
- 🖼️ **Logo personalizado** - LogoAdmin.png en todas las páginas del panel
- 🎯 **Navegación mejorada** - Dropdown con zona invisible para hover suave
- 👤 **Perfil de administrador separado** - Vista especial en `/admin-perfil/` con:
  - Información del administrador (nombre, email, teléfono)
  - Badge "ADMINISTRADOR" con gradiente azul
  - Botón destacado "Cerrar Sesión"
  - Sin opciones de editar perfil o eliminar cuenta
- 🔵 **Botones estandarizados**:
  - Azul (Primary) - Acciones principales
  - Amarillo (Back) - Volver/Retroceder
  - Rojo (Cancel) - Cancelar/Eliminar
- ✨ **Transiciones suaves** - Efectos hover y animaciones en todos los elementos

### Dashboard (`/admin-panel/`)
- 📊 Estadísticas generales:
  - Total de pedidos
  - Total de productos
  - Total de usuarios
- 🔗 Accesos rápidos a cada sección

### Gestión de Pedidos (`/admin-panel/pedidos/`)
- 📋 **Lista completa de pedidos** ordenados por fecha de creación
- 🏷️ **Badges de estado** con colores específicos:
  - 🟡 Pendiente (amarillo)
  - 🔵 Confirmado (azul claro)
  - 🟣 Procesando (índigo)
  - 🟪 Enviado (púrpura)
  - 🟢 Entregado (verde)
  - 🔴 Cancelado (rojo)
- 🔄 **Cambio de estado** mediante select dropdown con submit automático
- 🗑️ **Eliminar pedidos** con confirmación JavaScript
- 📦 Información visible:
  - Número de pedido
  - Cliente
  - Fecha de creación
  - Total
  - Estado actual

### Gestión de Productos (`/admin-panel/productos/`)
- 📝 **CRUD completo** de productos
- 🔍 **Sistema de filtrado avanzado**:
  - Búsqueda por nombre/descripción (barra expandida)
  - Multi-select de categorías con scrollbar azul personalizado
  - Multi-select de marcas con scrollbar azul personalizado
  - **Slider dual de rango de precio** interactivo:
    - Thumbs de 22px con gradiente azul
    - Track de 10px con barra de progreso visual
    - Labels dinámicos mostrando €min y €max
    - Intercambio automático de valores si min > max
    - Cálculo automático del rango desde la base de datos
  - Botón "Filtrar" (azul) y "Limpiar" (rojo) con efectos hover
  - Layout responsive en 3 filas para óptima usabilidad
- ➕ **Crear producto** (`/admin-panel/productos/crear/`):
  - Todos los campos del producto (precio único simplificado)
  - Vista previa de imagen al cargar
  - Selección de categoría y marca
  - **Creación inline de categorías/marcas**: Botones "+ Nueva" junto a selects
  - Checkbox "Es destacado"
- ✏️ **Editar producto** (`/admin-panel/productos/<id>/editar/`):
  - Mismas funcionalidades que crear
  - Imagen actual visible
  - Vista previa de nueva imagen
  - **Creación inline de categorías/marcas** también disponible
- 🗑️ **Eliminar producto** con confirmación:
  - Botón de papelera consistente con otras secciones admin
  - Confirmación JavaScript antes de eliminar
  - Eliminación en cascada de imágenes asociadas
- 🖼️ **Gestión de imágenes**:
  - Contenedores de altura fija (280px)
  - Vista previa inmediata con FileReader API
  - object-fit: contain para mantener proporciones
- 🎯 **Características especiales**:
  - Overflow de página oculto (solo scroll en tabla)
  - Imágenes en miniatura (50x50px) en tabla
  - Botones de acción con iconos
  - Formularios con validación cliente

### Gestión de Usuarios (`/admin-panel/usuarios/`)
- 👥 **Lista de todos los usuarios** con información completa
- ➕ **Crear usuario** (`/admin-panel/usuarios/crear/`):
  - Formulario completo: email, nombre, apellidos, teléfono, dirección, ciudad, código postal
  - Validación de email único
  - Contraseña requerida (mínimo 6 caracteres)
  - Layout con form-row para campos en línea
- ✏️ **Editar usuario** (`/admin-panel/usuarios/<id>/editar/`):
  - Todos los campos editables
  - Contraseña opcional (mantiene actual si se deja en blanco)
  - Validación de email único excluyendo usuario actual
  - Editable incluso para el usuario actual
- 🗑️ **Eliminar usuarios** con confirmación
  - Protección: no se puede auto-eliminar
  - Icono de papelera con estilo consistente
- 📊 Información visible:
  - ID
  - Email
  - Nombre completo
  - Fecha de creación

### Estilos y UX
- 🎨 **Paleta de colores**:
  - Azul principal: `#60A5FA → #3B82F6` (gradientes)
  - Amarillo (back): `#FCD34D → #F59E0B`
  - Rojo (cancel/delete): `#F87171 → #DC2626`
  - Azul oscuro (iconos): `#1E3A8A`
- 🖱️ **Efectos interactivos**:
  - Transform translateY(-1px) en hover
  - Box-shadow con color del botón (0.3 opacity)
  - Transiciones de 0.2s en todos los elementos
- 📱 **Responsive** - Adaptación a diferentes tamaños de pantalla
- ⚡ **Confirmaciones** - Diálogos JavaScript antes de eliminaciones

### Seguridad
- ✅ Verificación de autenticación en todas las vistas
- ✅ Validación de permisos de administrador
- ✅ Protección CSRF en todos los formularios POST
- ✅ Redirección a login si no autenticado
- ✅ Redirección a mainPage si no es admin
- ✅ Prevención de auto-modificación/eliminación

### Rutas del Panel
```python
/admin-panel/                                    # Dashboard
/admin-perfil/                                   # Perfil de administrador
/admin-panel/pedidos/                            # Lista de pedidos
/admin-panel/pedidos/<id>/estado/                # Cambiar estado
/admin-panel/pedidos/<id>/eliminar/              # Eliminar pedido
/admin-panel/productos/                          # Lista de productos (con filtros)
/admin-panel/productos/crear/                    # Crear producto
/admin-panel/productos/<id>/editar/              # Editar producto
/admin-panel/productos/<id>/eliminar/            # Eliminar producto
/admin-panel/usuarios/                           # Lista de usuarios
/admin-panel/usuarios/crear/                     # Crear usuario
/admin-panel/usuarios/<id>/editar/               # Editar usuario
/admin-panel/usuarios/<id>/eliminar/             # Eliminar usuario
```

## Compra Rápida (1-Click Checkout)

Sistema de compra simplificado que permite adquirir productos sin pasar por el carrito:

### Características
- ⚡ **Acceso directo** - Botón "⚡ Compra Rápida" destacado en listado de productos
- 📋 **Formulario unificado** - Todos los datos en una sola página:
  - Información personal (nombre, apellidos, email, teléfono)
  - Tipo de entrega (domicilio/tienda) con SVG icons
  - Dirección de envío (condicional según tipo de entrega)
  - Método de pago (tarjeta/contra reembolso)
- 🔢 **Selector de cantidad** - Botones +/- con validación de stock
- 💰 **Cálculos dinámicos en tiempo real**:
  - Subtotal actualizado por cantidad
  - IVA (21%)
  - Coste de envío (€5.99 o GRATIS si >€50)
  - Total final
  - Banners informativos de envío gratis
- 🎨 **Diseño consistente** - Tema verde corporativo matching con el sitio
- 💳 **Integración Braintree** - Drop-in UI para pago seguro con tarjeta
- ✅ **Pedido inmediato** - Estado "confirmado" desde el inicio
- 📧 **Email informativo** - Sin token de confirmación, directamente confirmado
- 📦 **Reducción de stock automática** - Inventario actualizado al confirmar

### Ventajas vs Checkout Normal
- Sin necesidad de agregar al carrito
- Un solo paso en lugar de tres
- Proceso más rápido para compra de un solo producto
- Ideal para usuarios que saben exactamente qué quieren
- Perfecto para mobile con menos navegación

### Flujo de Compra Rápida
1. Usuario hace click en "⚡ Compra Rápida" en producto
2. Formulario cargado con datos del usuario (si está autenticado)
3. Selecciona cantidad, tipo de entrega y método de pago
4. Ve totales actualizados en tiempo real
5. Click en "Confirmar Pedido"
6. Pedido creado como "confirmado"
7. Stock reducido inmediatamente
8. Email informativo enviado
9. Redirección a página de confirmación

### Diferencias Técnicas con Checkout Normal
- **Estado inicial**: `confirmado` vs `pendiente`
- **Token confirmación**: No se genera (campo vacío)
- **Email**: Informativo sin botón de confirmar
- **Stock**: Se reduce inmediatamente, no en confirmación posterior
- **Carrito**: No involucrado en el proceso
- **Pasos**: 1 formulario unificado vs 3 pasos secuenciales
