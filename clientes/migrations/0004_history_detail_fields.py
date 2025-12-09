from django.db import migrations, models


def copy_history_reasons(apps, schema_editor):
    ClientHistory = apps.get_model("clientes", "ClientHistory")
    for history in ClientHistory.objects.all().order_by("pk"):
        fields_to_update = []
        if getattr(history, "razao_saida", None):
            history.razao = history.razao_saida
            fields_to_update.append("razao")
        if getattr(history, "motivo_saida", None):
            history.motivo = history.motivo_saida
            if "motivo" not in fields_to_update:
                fields_to_update.append("motivo")
        if fields_to_update:
            history.save(update_fields=fields_to_update)


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0003_alter_client_options_alter_clienthistory_options"),
    ]

    operations = [
        migrations.RenameField(
            model_name="clienthistory",
            old_name="responsavel_anterior",
            new_name="responsavel_antigo",
        ),
        migrations.RenameField(
            model_name="clienthistory",
            old_name="data_transicao",
            new_name="data",
        ),
        migrations.AddField(
            model_name="clienthistory",
            name="razao",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="clienthistory",
            name="status_antigo",
            field=models.CharField(blank=True, max_length=7),
        ),
        migrations.AddField(
            model_name="clienthistory",
            name="status_novo",
            field=models.CharField(blank=True, max_length=7),
        ),
        migrations.AddField(
            model_name="clienthistory",
            name="termometro_antigo",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="clienthistory",
            name="termometro_novo",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="clienthistory",
            name="valor_antigo",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="clienthistory",
            name="valor_novo",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="clienthistory",
            name="permuta_antiga",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="clienthistory",
            name="permuta_nova",
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="clienthistory",
            name="responsavel_antigo",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.RunPython(copy_history_reasons, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="clienthistory",
            name="motivo_saida",
        ),
        migrations.RemoveField(
            model_name="clienthistory",
            name="razao_saida",
        ),
        migrations.AlterModelOptions(
            name="clienthistory",
            options={"ordering": ["-data"]},
        ),
    ]
