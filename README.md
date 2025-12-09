# Sistema de Gestão de Clientes (Django)

Este projeto é uma reimplementação em Django do sistema React original. Ele mantém as mesmas funcionalidades: cadastro de clientes, transferências entre operadores, registro de saídas com motivos/razões e um dashboard consolidado com indicadores.

## Tecnologias

- Python 3.11+
- Django 5
- Bootstrap 5 (via CDN)
- SQLite (default)

## Como rodar localmente

```bash
cd gestao_clientes
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # opcional
python manage.py runserver
```

Acesse http://127.0.0.1:8000 para usar o app ou http://127.0.0.1:8000/admin para gerenciar dados pelo Django Admin.

## Funcionalidades principais

- **Dashboard** com totais de clientes, receita ativa, operadores, tabela por responsável e histórico recente.
- **Lista de clientes** com filtros por nome, responsável, status e termômetro; ordenação customizável e botões para editar, transferir, marcar saída ou remover.
- **Cadastro/Edição** de clientes com campos equivalentes ao SPA: nome, termômetro (1–5), responsável, status, datas de entrada/saída, valor, permuta e observações.
- **Transferências** entre responsáveis com histórico automático e motivos reutilizáveis.
- **Registro de saída** com data, motivo, razão e atualização automática do status para `INATIVO`.
- **Importação** via CSV (mesmo cabeçalho usado no frontend).
- **Gestão de referências** (responsáveis, motivos/razões de saída e motivos de transferência) para alimentar os campos com sugestões.
- **Relatórios por operador** e **receita mensal** calculados a partir do histórico de clientes, replicando as métricas exibidas no dashboard original.

## Estrutura

- `clientes/models.py`: modelos de negócio (`Client`, `ClientHistory`, `Responsavel`, etc.).
- `clientes/forms.py`: formulários para clientes, transferências, saídas, importação e cadastros auxiliares.
- `clientes/views.py`: views para dashboard, CRUD, transferências, importação e configurações.
- `clientes/utils.py`: funções que reproduzem os relatórios mensais e o controle de responsáveis por período.
- `templates/` + `static/`: layout base em Bootstrap e telas equivalentes às do React.

## Próximos passos sugeridos

- Criar testes automatizados para o fluxo de transferências/saídas.
- Expandir a importação para aceitar XLSX ou planilhas Lovable.
- Guardar arquivos enviados e gerar logs/auditorias via Admin.
