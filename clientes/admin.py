from django.contrib import admin

from .models import Client, ClientHistory, Consultor, Motivo, Razao, Responsavel, ReuniaoPreferencia


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("nome", "responsavel", "status", "entrada", "valor", "permuta")
    list_filter = ("status", "responsavel", "permuta")
    search_fields = ("nome", "responsavel")
    ordering = ("-entrada",)


@admin.register(ClientHistory)
class ClientHistoryAdmin(admin.ModelAdmin):
    list_display = ("client", "tipo", "data", "descricao_alteracao", "motivo", "razao")
    list_filter = ("tipo", "data")
    search_fields = (
        "client__nome",
        "responsavel_antigo",
        "responsavel_novo",
        "motivo",
        "razao",
    )


@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "ativo", "criado_em")
    search_fields = ("nome", "email")
    list_filter = ("ativo",)


@admin.register(Motivo)
class MotivoAdmin(admin.ModelAdmin):
    list_display = ("nome", "criado_em")
    search_fields = ("nome",)


@admin.register(Razao)
class RazaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "motivo", "tipo_de_historico", "criado_em")
    list_filter = ("tipo_de_historico", "motivo")
    search_fields = ("nome", "motivo__nome")


@admin.register(Consultor)
class ConsultorAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "ativo", "criado_em")
    list_filter = ("ativo",)
    search_fields = ("nome", "email")


@admin.register(ReuniaoPreferencia)
class ReuniaoPreferenciaAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "tipo",
        "dia_pref_inicio",
        "dia_pref_fim",
        "dia_semana_pref",
        "horario_pref",
        "local",
        "data_sugerida",
        "consultor",
        "atualizado_em",
    )
    list_filter = ("tipo", "horario_pref", "local", "dia_semana_pref")
    search_fields = ("client__nome", "consultor__nome", "responsavel_nome")
