import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_clientes.settings')
django.setup()

from django.contrib.auth.models import User, Group

def create_superuser():
    username = 'admin'
    password = '1234'
    email = 'admin@example.com'

    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f'Usuário "{username}" já existe.')
        
        # Garantir que o usuário tenha is_staff=True
        if not user.is_staff:
            user.is_staff = True
            user.save()
            print(f'Configurado is_staff=True para "{username}".')
        
        # Garantir que o usuário esteja no grupo Administrador
        admin_group, _ = Group.objects.get_or_create(name='Administrador')
        if not user.groups.filter(name='Administrador').exists():
            user.groups.add(admin_group)
            print(f'Usuário "{username}" adicionado ao grupo "Administrador".')
        else:
            print(f'Usuário "{username}" já está no grupo "Administrador".')
    else:
        user = User.objects.create_superuser(username=username, password=password, email=email)
        print(f'Superusuário "{username}" criado com sucesso.')
        
        # Adicionar ao grupo Administrador
        admin_group, _ = Group.objects.get_or_create(name='Administrador')
        user.groups.add(admin_group)
        print(f'Usuário "{username}" adicionado ao grupo "Administrador".')

if __name__ == '__main__':
    create_superuser()
