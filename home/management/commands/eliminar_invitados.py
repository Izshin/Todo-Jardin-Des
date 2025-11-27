from django.core.management.base import BaseCommand
from home.models import Cliente, Carrito

class Command(BaseCommand):
    help = 'Elimina todos los usuarios invitados ANTIGUOS y TEMPORALES (sin contraseña o con nombre "Invitado"), pero preserva la cuenta de invitado del sistema (invitado@sistema.local)'

    def handle(self, *args, **options):
        # Email de la cuenta de invitado del sistema que NO debe eliminarse
        EMAIL_INVITADO_SISTEMA = 'invitado@sistema.local'
        
        # Buscar usuarios invitados ANTIGUOS y TEMPORALES (excluyendo la cuenta del sistema)
        invitados = Cliente.objects.filter(
            nombre='Invitado'
        ).filter(
            password=''
        ).exclude(
            email=EMAIL_INVITADO_SISTEMA
        ) | Cliente.objects.filter(
            password__isnull=True
        ).exclude(
            email=EMAIL_INVITADO_SISTEMA
        ) | Cliente.objects.filter(
            email__endswith='@temporal.local'
        )
        
        count = invitados.count()
        
        if count > 0:
            self.stdout.write(f'Encontrados {count} usuarios invitados')
            
            # Eliminar carritos asociados
            for invitado in invitados:
                Carrito.objects.filter(cliente=invitado).delete()
            
            # Eliminar invitados
            invitados.delete()
            
            self.stdout.write(self.style.SUCCESS(f'✓ Eliminados {count} usuarios invitados exitosamente'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ No se encontraron usuarios invitados'))
