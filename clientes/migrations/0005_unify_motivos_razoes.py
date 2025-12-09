import django.db.models.deletion
from django.db import migrations, models


def migrate_motivos_razoes(apps, schema_editor):
    MotivoSaida = apps.get_model("clientes", "MotivoSaida")
    RazaoSaida = apps.get_model("clientes", "RazaoSaida")
    MotivoTransferencia = apps.get_model("clientes", "MotivoTransferencia")
    Motivo = apps.get_model("clientes", "Motivo")
    Razao = apps.get_model("clientes", "Razao")

    def ensure_motivo(nome: str | None):
        nome = (nome or "").strip()
        if not nome:
            return None
        motivo, _ = Motivo.objects.get_or_create(nome=nome)
        return motivo

    legado = ensure_motivo("Motivo legado")

    for registro in MotivoSaida.objects.all():
        ensure_motivo(registro.descricao)

    for registro in MotivoTransferencia.objects.all():
        ensure_motivo(registro.descricao)

    for registro in RazaoSaida.objects.all():
        motivo = ensure_motivo(registro.descricao) or legado
        if motivo is None:
            continue
        Razao.objects.get_or_create(
            nome=registro.descricao,
            tipo_de_historico="registro_de_saida",
            defaults={"motivo": motivo},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("clientes", "0004_history_detail_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="Motivo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("nome", models.CharField(max_length=150, unique=True)),
            ],
            options={"ordering": ["nome"]},
        ),
        migrations.CreateModel(
            name="Razao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("nome", models.CharField(max_length=150)),
                (
                    "tipo_de_historico",
                    models.CharField(
                        choices=[
                            ("transferencia", "Transferência"),
                            ("alteracao_de_valor", "Alteração de valor"),
                            ("registro_de_saida", "Registro de saída"),
                            ("alteracao_de_termometro", "Alteração de termômetro"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "motivo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="razoes",
                        to="clientes.motivo",
                    ),
                ),
            ],
            options={"ordering": ["nome"], "unique_together": {("nome", "tipo_de_historico")}},
        ),
        migrations.RunPython(migrate_motivos_razoes, migrations.RunPython.noop),
        migrations.DeleteModel(name="RazaoSaida"),
        migrations.DeleteModel(name="MotivoTransferencia"),
        migrations.DeleteModel(name="MotivoSaida"),
    ]
