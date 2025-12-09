from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0009_alter_reuniaopreferencia_local"),
    ]

    operations = [
        migrations.AddField(
            model_name="reuniaopreferencia",
            name="dia_semana_pref",
            field=models.CharField(
                blank=True,
                choices=[
                    ("SEGUNDA", "Segunda-feira"),
                    ("TERCA", "Terça-feira"),
                    ("QUARTA", "Quarta-feira"),
                    ("QUINTA", "Quinta-feira"),
                    ("SEXTA", "Sexta-feira"),
                    ("SABADO", "Sábado"),
                    ("DOMINGO", "Domingo"),
                ],
                default="",
                max_length=15,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="reuniaopreferencia",
            name="observacoes",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="reuniaopreferencia",
            name="dia_pref_fim",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(31),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="reuniaopreferencia",
            name="dia_pref_inicio",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(31),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="reuniaopreferencia",
            name="data_sugerida",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(31),
                ],
            ),
        ),
    ]
