from django.core.management.base import BaseCommand
from home.models import Cliente

class Command(BaseCommand):
    help = 'Crea o verifica la existencia de la cuenta de invitado del sistema'

    def handle(self, *args, **options):
        # Email especial para identificar la cuenta de invitado del sistema
        EMAIL_INVITADO = 'invitado@sistema.local'
        
        # Intentar obtener la cuenta de invitado
        invitado, created = Cliente.objects.get_or_create(
            email=EMAIL_INVITADO,
            defaults={
                'nombre': 'Invitado',
                'apellidos': 'Sistema',
                'telefono': '000000000',
                'direccion': 'N/A',
                'ciudad': 'N/A',
                'codigo_postal': '00000',
                'password': ''  # Sin contraseña
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Cuenta de invitado del sistema creada exitosamente (ID: {invitado.id})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Cuenta de invitado del sistema ya existe (ID: {invitado.id})'))
