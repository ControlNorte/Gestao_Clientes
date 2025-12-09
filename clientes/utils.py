from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Dict, Iterable, List, Tuple

from .models import Client, ClientHistory


def month_key_from_date(value: date) -> str:
    return value.strftime("%Y-%m")


def month_start(value: date) -> date:
    return date(value.year, value.month, 1)


def previous_month(value: date) -> date:
    year = value.year
    month = value.month - 1
    if month == 0:
        month = 12
        year -= 1
    return date(year, month, 1)


def add_months(value: date, months: int) -> date:
    month = value.month - 1 + months
    year = value.year + month // 12
    month = month % 12 + 1
    return date(year, month, 1)


def month_str_to_date(month_str: str) -> date:
    year, month = month_str.split("-")
    return date(int(year), int(month), 1)


def iterate_months(start: date, end: date) -> Iterable[date]:
    current = month_start(start)
    end_month = month_start(end)
    while current <= end_month:
        yield current
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)


def get_responsavel_no_mes(
    client: Client, mes_ano: str, transferencias: List[ClientHistory] | None = None
) -> str:
    """Return the responsible agent for the client in a given YYYY-MM period."""
    if transferencias is None:
        transferencias = sorted(
            (h for h in client.historico.all() if h.tipo == "TRANSFERENCIA"),
            key=lambda hist: hist.data,
        )

    if not transferencias:
        return client.responsavel

    responsavel = transferencias[0].responsavel_antigo or client.responsavel
    for transferencia in transferencias:
        hist_mes = transferencia.data.strftime("%Y-%m")
        if hist_mes <= mes_ano:
            responsavel = transferencia.responsavel_novo or responsavel
        else:
            break
    return responsavel


def build_operator_reports(clients: Iterable[Client]) -> Dict[str, object]:
    """Create structures that mimic the dashboard reports from the React app."""
    operator_data: Dict[str, Dict[str, Dict[str, Decimal]]] = {}
    operator_counts: Dict[str, Dict[str, Dict[str, Decimal]]] = {}
    months: set[str] = set()
    monthly_revenue: Dict[str, Dict[str, Decimal]] = defaultdict(
        lambda: {"total": Decimal("0"), "ativos": Decimal("0"), "inativos": Decimal("0")}
    )

    today_month = month_start(date.today())

    def ensure_operator(resp: str) -> None:
        operator_data.setdefault(
            resp,
            {
                "entradas": defaultdict(lambda: {"quantidade": 0, "valor": Decimal("0")}),
                "saidas": defaultdict(lambda: {"quantidade": 0, "valor": Decimal("0")}),
                "ativos": defaultdict(lambda: {"quantidade": 0, "valor": Decimal("0")}),
            },
        )
        operator_counts.setdefault(
            resp,
            {"ativos": 0, "inativos": 0, "valor_total": Decimal("0")},
        )

    for client in clients:
        transferencias = sorted(
            (h for h in client.historico.all() if h.tipo == "TRANSFERENCIA"),
            key=lambda hist: hist.data,
        )
        entrada_mes = month_key_from_date(client.entrada)
        months.add(entrada_mes)
        resp_entrada = get_responsavel_no_mes(client, entrada_mes, transferencias)
        ensure_operator(resp_entrada)
        entry_bucket = operator_data[resp_entrada]["entradas"][entrada_mes]
        entry_bucket["quantidade"] += 1

        value_start_month_date = add_months(month_start(client.entrada), 1)
        value_start_key = month_key_from_date(value_start_month_date)
        last_value_month_date = previous_month(client.saida) if client.saida else None
        can_register_value_entry = not client.saida or value_start_month_date <= last_value_month_date
        if can_register_value_entry and value_start_month_date <= today_month:
            months.add(value_start_key)
            ensure_operator(resp_entrada)
            value_entry_bucket = operator_data[resp_entrada]["entradas"][value_start_key]
            value_entry_bucket["valor"] += client.valor

        current_responsavel = resp_entrada
        for transferencia in transferencias:
            mes_transferencia = month_key_from_date(transferencia.data)
            months.add(mes_transferencia)
            resp_antigo = transferencia.responsavel_antigo or current_responsavel
            resp_novo = transferencia.responsavel_novo or resp_antigo
            ensure_operator(resp_antigo)
            ensure_operator(resp_novo)
            transfer_exit_bucket = operator_data[resp_antigo]["saidas"][mes_transferencia]
            transfer_exit_bucket["quantidade"] += 1
            transfer_exit_bucket["valor"] += client.valor
            transfer_entry_bucket = operator_data[resp_novo]["entradas"][mes_transferencia]
            transfer_entry_bucket["quantidade"] += 1
            transfer_entry_bucket["valor"] += client.valor
            current_responsavel = resp_novo

        if client.saida:
            saida_mes = month_key_from_date(client.saida)
            months.add(saida_mes)
            resp_saida = get_responsavel_no_mes(client, saida_mes, transferencias)
            ensure_operator(resp_saida)
            exit_bucket = operator_data[resp_saida]["saidas"][saida_mes]
            exit_bucket["quantidade"] += 1
            exit_bucket["valor"] += client.valor

        # Valores ativos
        start_month = month_start(client.entrada)
        if client.saida:
            end_month = previous_month(client.saida)
            if end_month < start_month:
                end_month = start_month
        else:
            end_month = today_month

        for month_date in iterate_months(start_month, end_month):
            mes = month_key_from_date(month_date)
            months.add(mes)
            responsavel_no_mes = get_responsavel_no_mes(client, mes, transferencias)
            ensure_operator(responsavel_no_mes)
            ativa_bucket = operator_data[responsavel_no_mes]["ativos"][mes]
            ativa_bucket["quantidade"] += 1
            ativo_valor = client.valor if month_date >= value_start_month_date else Decimal("0")
            ativa_bucket["valor"] += ativo_valor

            revenue_bucket = monthly_revenue[mes]
            if ativo_valor:
                revenue_bucket["total"] += ativo_valor
                if client.status == "ATIVO":
                    revenue_bucket["ativos"] += ativo_valor
                else:
                    revenue_bucket["inativos"] += ativo_valor

        responsavel_atual = client.responsavel
        ensure_operator(responsavel_atual)
        if client.status == "ATIVO":
            operator_counts[responsavel_atual]["ativos"] += 1
        else:
            operator_counts[responsavel_atual]["inativos"] += 1
        operator_counts[responsavel_atual]["valor_total"] += client.valor

    sorted_months = sorted(months)
    normalized_operators: Dict[str, Dict[str, Dict[str, Decimal]]] = {}
    for resp, info in operator_data.items():
        normalized_operators[resp] = {
            "entradas": dict(info["entradas"]),
            "saidas": dict(info["saidas"]),
            "ativos": dict(info["ativos"]),
        }

    normalized_revenue = {mes: monthly_revenue[mes] for mes in sorted_months if mes in monthly_revenue}

    total_quantity_by_month = {mes: 0 for mes in sorted_months}
    total_entries_by_month = {mes: 0 for mes in sorted_months}
    total_exits_by_month = {mes: 0 for mes in sorted_months}

    quantity_rows = []
    for resp in sorted(normalized_operators.keys()):
        info = normalized_operators[resp]
        running = 0
        series = []
        for mes in sorted_months:
            entry_qty = info["entradas"].get(mes, {}).get("quantidade", 0)
            exit_qty = info["saidas"].get(mes, {}).get("quantidade", 0)
            running = running + entry_qty - exit_qty
            if running < 0:
                running = 0
            series.append(
                {
                    "month": mes,
                    "cumulative": running,
                    "entries": entry_qty,
                    "exits": exit_qty,
                }
            )
            total_entries_by_month[mes] += entry_qty
            total_exits_by_month[mes] += exit_qty
            total_quantity_by_month[mes] += running
        quantity_rows.append({"name": resp, "series": series})

    quantity_totals = [
        {
            "month": mes,
            "cumulative": total_quantity_by_month[mes],
            "entries": total_entries_by_month[mes],
            "exits": total_exits_by_month[mes],
        }
        for mes in sorted_months
    ]

    total_value_by_month = {mes: Decimal("0") for mes in sorted_months}
    total_value_entries_by_month = {mes: Decimal("0") for mes in sorted_months}
    total_value_exits_by_month = {mes: Decimal("0") for mes in sorted_months}

    value_rows = []
    for resp in sorted(normalized_operators.keys()):
        info = normalized_operators[resp]
        running = Decimal("0")
        series = []
        for mes in sorted_months:
            entry_value = info["entradas"].get(mes, {}).get("valor", Decimal("0"))
            exit_value = info["saidas"].get(mes, {}).get("valor", Decimal("0"))
            running = running + entry_value - exit_value
            if running < 0:
                running = Decimal("0")
            series.append(
                {
                    "month": mes,
                    "cumulative": running,
                    "entries": entry_value,
                    "exits": exit_value,
                }
            )
            total_value_entries_by_month[mes] += entry_value
            total_value_exits_by_month[mes] += exit_value
            total_value_by_month[mes] += running
        value_rows.append({"name": resp, "series": series})

    value_totals = [
        {
            "month": mes,
            "cumulative": total_value_by_month[mes],
            "entries": total_value_entries_by_month[mes],
            "exits": total_value_exits_by_month[mes],
        }
        for mes in sorted_months
    ]

    # Relatório por cliente (recebimentos)
    def parse_iso(value) -> date | None:
        if not value:
            return None
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value))

    entry_count = {mes: 0 for mes in sorted_months}
    entry_value = {mes: Decimal("0") for mes in sorted_months}
    exit_count = {mes: 0 for mes in sorted_months}
    exit_value = {mes: Decimal("0") for mes in sorted_months}
    active_count = {mes: 0 for mes in sorted_months}
    active_value = {mes: Decimal("0") for mes in sorted_months}

    client_rows = []
    for client in sorted(clients, key=lambda c: c.nome):
        entrada_date = parse_iso(client.entrada) or date.today()
        receipt_start = add_months(month_start(entrada_date), 1)
        receipt_end = None
        if client.saida:
            receipt_end = month_start(parse_iso(client.saida))

        start_month_key = month_key_from_date(receipt_start)
        if start_month_key in entry_count:
            entry_count[start_month_key] += 1
            entry_value[start_month_key] += client.valor

        if receipt_end:
            exit_month_key = month_key_from_date(receipt_end)
            if exit_month_key in exit_count:
                exit_count[exit_month_key] += 1
                exit_value[exit_month_key] += client.valor

        row_values = []
        total_row = Decimal("0")
        for mes in sorted_months:
            month_date = month_str_to_date(mes)
            receives = month_date >= receipt_start and (
                not receipt_end or month_date < receipt_end
            )
            value = client.valor if receives else Decimal("0")
            row_values.append(value)
            if receives:
                total_row += value
                active_count[mes] += 1
                active_value[mes] += value
        client_rows.append({"name": client.nome, "values": row_values, "total": total_row})

    def values_list(data: Dict[str, Decimal] | Dict[str, int]) -> List:
        return [data[mes] for mes in sorted_months]

    client_cashflow_report = {
        "months": sorted_months,
        "rows": client_rows,
        "summary": {
            "total_value": values_list(active_value),
            "active": {
                "count": values_list(active_count),
                "value": values_list(active_value),
            },
            "entries": {
                "count": values_list(entry_count),
                "value": values_list(entry_value),
            },
            "exits": {
                "count": values_list(exit_count),
                "value": values_list(exit_value),
            },
        },
    }

    return {
        "months": sorted_months,
        "operators": normalized_operators,
        "operator_totals": operator_counts,
        "monthly_revenue": normalized_revenue,
        "quantity_report": {
            "rows": quantity_rows,
            "monthly_totals": quantity_totals,
        },
        "value_report": {
            "rows": value_rows,
            "monthly_totals": value_totals,
        },
        "client_cashflow_report": client_cashflow_report,
    }
