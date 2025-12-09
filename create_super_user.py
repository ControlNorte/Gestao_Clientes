import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestao_clientes.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    username = 'admin'
    password = '1234'
    email = 'admin@example.com'

    if User.objects.filter(username=username).exists():
        print(f'Usuário "{username}" já existe.')
    else:
        User.objects.create_superuser(username=username, password=password, email=email)
        print(f'Superusuário "{username}" criado com sucesso.')

if __name__ == '__main__':
    create_superuser()
