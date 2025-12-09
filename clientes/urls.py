from django.urls import path

from . import views

app_name = "clientes"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("clientes/", views.client_list, name="client_list"),
    path("clientes/reunioes/", views.reunioes_lista, name="reunioes_lista"),
    path("clientes/reunioes/exportar/", views.reunioes_export, name="reunioes_export"),
    path("financeiro/", views.financeiro_view, name="financeiro"),
    path("usuarios/", views.usuarios_view, name="usuarios"),
    path("clientes/novo/", views.client_create, name="client_create"),
    path("clientes/<int:pk>/editar/", views.client_update, name="client_update"),
    path("clientes/<int:pk>/excluir/", views.client_delete, name="client_delete"),
    path("clientes/<int:pk>/transferir/", views.transfer_client, name="client_transfer"),
    path("clientes/<int:pk>/saida/", views.exit_client, name="client_exit"),
    path("clientes/<int:pk>/termometro/", views.change_termometro, name="client_termometro"),
    path("clientes/<int:pk>/valor/", views.change_valor, name="client_value"),
    path("clientes/exportar/", views.client_export, name="client_export"),
    path("clientes/importar/", views.import_clients, name="client_import"),
    path("config/responsaveis/", views.manage_responsaveis, name="responsaveis"),
    path("config/consultores/", views.manage_consultores, name="consultores"),
    path("config/motivos-razoes/", views.manage_motivos_razoes, name="motivos_razoes"),
    path("clientes/<int:pk>/reunioes/preferencias/", views.manage_reuniao_preferencias, name="reuniao_preferencias"),
    path("config/limpar/", views.clear_database, name="clear_database"),
    path("agendamentos/", views.agendamentos_view, name="agendamentos"),
    path("agendamentos/api/list/", views.agendamentos_api_list, name="agendamentos_api_list"),
    path("agendamentos/api/save/", views.agendamentos_api_save, name="agendamentos_api_save"),
    path("acesso-negado/", views.acesso_negado, name="acesso_negado"),
]
