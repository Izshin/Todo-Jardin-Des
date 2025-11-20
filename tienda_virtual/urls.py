"""
URL configuration for tienda_virtual project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from home import views

urlpatterns = [
    path('', views.mainPage, name='mainPage'),
    path('terminos/', views.terminos, name='terminos'),
    path('user/', views.user, name='user'),
    path('login/', views.login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('logout/', views.logout, name='logout'),
    path('eliminar-cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),
    path('productos/', views.productos, name='productos'),
    path('producto/<int:producto_id>/', views.producto_detalle, name='producto_detalle'),
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/comprar-ahora/<int:producto_id>/', views.comprar_ahora, name='comprar_ahora'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/paso2/', views.checkout_paso2, name='checkout_paso2'),
    path('checkout/paso3/', views.checkout_paso3, name='checkout_paso3'),
    path('procesar-pago/', views.procesar_pago, name='procesar_pago'),
    path('confirmacion/<int:pedido_id>/', views.confirmacion_pedido, name='confirmacion_pedido'),
    path('confirmar-pedido/<int:pedido_id>/', views.confirmar_pedido, name='confirmar_pedido'),
    path('mis-pedidos/', views.historial_pedidos, name='historial_pedidos'),
    path('establecer-password/', views.establecer_password, name='establecer_password'),
    path('buscar-pedido/', views.buscar_pedido, name='buscar_pedido'),
    
    # Admin URLs
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/pedidos/', views.admin_pedidos, name='admin_pedidos'),
    path('admin-panel/pedidos/<int:pedido_id>/estado/', views.admin_actualizar_estado_pedido, name='admin_actualizar_estado_pedido'),
    path('admin-panel/pedidos/<int:pedido_id>/eliminar/', views.admin_eliminar_pedido, name='admin_eliminar_pedido'),
    path('admin-panel/productos/', views.admin_productos, name='admin_productos'),
    path('admin-panel/productos/crear/', views.admin_crear_producto, name='admin_crear_producto'),
    path('admin-panel/productos/<int:producto_id>/editar/', views.admin_editar_producto, name='admin_editar_producto'),
    path('admin-panel/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('admin-panel/usuarios/<int:usuario_id>/toggle-admin/', views.admin_toggle_admin, name='admin_toggle_admin'),
    path('admin-panel/usuarios/<int:usuario_id>/eliminar/', views.admin_eliminar_usuario, name='admin_eliminar_usuario'),
    
    path('admin/', admin.site.urls),
]

# Servir archivos de medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
