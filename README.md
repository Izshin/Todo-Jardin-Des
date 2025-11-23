# Todo Jardin - Tienda Virtual

Proyecto de tienda online de jardinería desarrollado en Django.

## Setup Inicial

### 1. Clonar el repositorio
```bash
git clone <url-del-repo>
cd PGPI-G2.10
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

- **Email:** maria.garcia@example.com  
  **Contraseña:** password123

- **Email:** juan.martinez@example.com  
  **Contraseña:** password123

- **Email:** ana.lopez@example.com  
  **Contraseña:** password123

## Funcionalidades

- ✅ Sistema de autenticación (registro, login, perfil, eliminar cuenta)
- ✅ **Compra rápida sin registro (PB-11)** - Checkout en 3 pasos como invitado
- ✅ **⚡ Compra Rápida de 1 Click** - Sistema de checkout simplificado sin pasar por el carrito
  - Botón destacado en listado de productos
  - Formulario unificado con todos los datos en una sola página
  - Selector de cantidad con botones +/-
  - Cálculo dinámico de totales en tiempo real
  - Pedidos creados directamente como "confirmados"
  - Email informativo sin necesidad de confirmación posterior
- ✅ **Búsqueda global (PB-10)** - Barra de búsqueda en todas las páginas
- ✅ **Rastreador de pedidos** - Sistema de búsqueda de pedidos sin registro
- ✅ Catálogo de productos con filtros (búsqueda, categoría, marca, **rango de precio con slider dual**)
- ✅ Detalle de productos con productos relacionados
- ✅ Productos destacados en página principal
- ✅ Carrito de compras (agregar, modificar cantidad, eliminar)
- ✅ Mini-carrito desplegable en navegación
- ✅ **Sistema de checkout en 3 pasos reales**
  - Paso 1: Información de envío y tipo de entrega (domicilio/tienda)
  - Paso 2: Método de pago con selector (tarjeta/contra reembolso)
  - Paso 3: Confirmación del pedido con datos completos
- ✅ **Integración de Braintree (PB-14)** - Pasarela de pago real
  - Drop-in UI para entrada segura de tarjetas
  - Tokenización de datos sensibles
  - Procesamiento real de transacciones
  - Sandbox para pruebas
- ✅ **Pago contra reembolso (PB-24)** - Opción de pago en efectivo al recibir
  - Selector de método de pago en checkout paso 2
  - Sin requerimiento de tarjeta para efectivo
  - Banner informativo en confirmación
- ✅ Confirmación de pedidos con resumen completo
- ✅ **Historial de pedidos** - Vista completa con estados y detalles
- ✅ **Emails de confirmación UTF-8** - Soporte completo para caracteres españoles (ñ, á, é, etc.)
- ✅ **Página de Términos y Condiciones** - Información legal y contacto
- ✅ **Seeder mejorado** - Recarga limpia de imágenes sin duplicados
- ✅ **Suite de Tests Completa** - 19 tests unitarios con cobertura completa

## Compra sin Registro (PB-11)

Los usuarios pueden realizar compras sin necesidad de crear una cuenta:

1. **Añadir al carrito** - Se crea automáticamente una sesión de invitado
2. **Paso 1: Datos de envío** - Formulario solicita información personal y de envío
3. **Paso 2: Método de pago** - Integración con Braintree para pago seguro
4. **Paso 3: Confirmación** - Revisión final antes de procesar
5. **Confirmación del pedido** - Pedido completado con número de seguimiento

**Características:**
- Cliente invitado temporal creado automáticamente
- Banner informativo sugiere crear cuenta para guardar pedidos
- Navegación con botón "Volver" entre pasos
- Indicadores visuales de progreso (1/3, 2/3, 3/3)
- Datos persistidos en sesión entre pasos

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
