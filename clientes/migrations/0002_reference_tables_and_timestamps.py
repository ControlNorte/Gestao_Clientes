# Generated manually to add reference tables and timestamp fields.
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clienthistory',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clienthistory',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='MotivoSaida',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('descricao', models.CharField(max_length=150, unique=True)),
            ],
            options={
                'ordering': ['descricao'],
                'verbose_name': 'Motivo de Saída',
                'verbose_name_plural': 'Motivos de Saída',
            },
        ),
        migrations.CreateModel(
            name='MotivoTransferencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('descricao', models.CharField(max_length=150, unique=True)),
            ],
            options={
                'ordering': ['descricao'],
                'verbose_name': 'Motivo de Transferência',
                'verbose_name_plural': 'Motivos de Transferência',
            },
        ),
        migrations.CreateModel(
            name='RazaoSaida',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('descricao', models.CharField(max_length=150, unique=True)),
            ],
            options={
                'ordering': ['descricao'],
                'verbose_name': 'Razão de Saída',
                'verbose_name_plural': 'Razões de Saída',
            },
        ),
        migrations.CreateModel(
            name='Responsavel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['nome'],
            },
        ),
    ]
