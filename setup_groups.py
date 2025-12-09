import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_clientes.settings')
django.setup()

from django.contrib.auth.models import Group

def setup_groups():
    groups = ['Administrador', 'Agendamento']
    for name in groups:
        group, created = Group.objects.get_or_create(name=name)
        if created:
            print(f'Grupo "{name}" criado com sucesso.')
        else:
            print(f'Grupo "{name}" já existe.')

if __name__ == '__main__':
    setup_groups()
