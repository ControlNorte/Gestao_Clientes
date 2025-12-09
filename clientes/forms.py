from __future__ import annotations

from datetime import date
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from .models import Client, Consultor, Motivo, Razao, Responsavel, ReuniaoPreferencia


TERMOMETRO_CHOICES = [(str(num), f"{num} ⭐") for num in range(1, 6)]


class BootstrapFormMixin:
    """Applies Bootstrap classes to default Django widgets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class ClientForm(BootstrapFormMixin, forms.ModelForm):
    responsavel = forms.ChoiceField(label="Responsável", choices=[])
    termometro = forms.ChoiceField(choices=TERMOMETRO_CHOICES, initial="3")

    class Meta:
        model = Client
        fields = [
            "nome",
            "responsavel",
            "quer_alinhamento",
            "termometro",
            "status",
            "entrada",
            "saida",
            "valor",
            "permuta",
            "motivo",
            "razao",
        ]
        widgets = {
            "entrada": forms.DateInput(attrs={"type": "date"}),
            "saida": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        responsavel_choices = kwargs.pop("responsavel_choices", None)
        include_exit_fields = kwargs.pop("include_exit_fields", True)
        super().__init__(*args, **kwargs)
        if responsavel_choices is None:
            responsavel_choices = list(
                Responsavel.objects.order_by("nome").values_list("nome", flat=True)
            )
        current_value = self.initial.get("responsavel") or getattr(self.instance, "responsavel", "")
        if current_value and current_value not in responsavel_choices:
            responsavel_choices = [current_value] + list(responsavel_choices)
        options = [("", "Selecione um responsável")] + [
            (valor, valor) for valor in responsavel_choices
        ]
        self.fields["responsavel"].choices = options
        self.fields["valor"].widget.attrs.setdefault("step", "0.01")
        self.fields["valor"].widget.attrs.setdefault("min", "0")
        self.show_exit_fields = include_exit_fields
        if not include_exit_fields:
            for field in ("saida", "motivo", "razao"):
                self.fields.pop(field, None)

    def clean_termometro(self) -> int:
        value = self.cleaned_data.get("termometro", "3")
        return int(value)

    def clean_quer_alinhamento(self) -> bool:
        return bool(self.cleaned_data.get("quer_alinhamento"))

    def clean_permuta(self) -> bool:
        return bool(self.cleaned_data.get("permuta"))

    def clean(self):
        cleaned = super().clean()
        permuta = cleaned.get("permuta")
        status = cleaned.get("status")
        valor = cleaned.get("valor")

        if permuta:
            cleaned["valor"] = Decimal("0")
        elif status == "INATIVO":
            if valor in (None, ""):
                cleaned["valor"] = Decimal("0")
        else:
            if valor is None or valor <= 0:
                raise ValidationError("O valor deve ser maior que zero para clientes ativos sem permuta.")

        return cleaned


class ClientBasicUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Client
        fields = ["nome", "quer_alinhamento"]

    def clean_quer_alinhamento(self) -> bool:
        return bool(self.cleaned_data.get("quer_alinhamento"))


class TransferForm(BootstrapFormMixin, forms.Form):
    novo_responsavel = forms.ChoiceField(label="Novo responsável", choices=[])
    motivo = forms.ChoiceField(label="Motivo da transferência", choices=[])
    razao = forms.ChoiceField(label="Razão", choices=[])
    data = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Data da transferência",
    )

    def __init__(self, *args, **kwargs):
        responsavel_choices = kwargs.pop("responsavel_choices", None)
        motivo_choices = kwargs.pop("motivo_choices", None)
        razao_choices = kwargs.pop("razao_choices", None)
        super().__init__(*args, **kwargs)
        if responsavel_choices is None:
            responsavel_choices = list(
                Responsavel.objects.order_by("nome").values_list("nome", flat=True)
            )
        options = [("", "Selecione um responsável")] + [(resp, resp) for resp in responsavel_choices]
        current_value = self.initial.get("novo_responsavel")
        if current_value and current_value not in responsavel_choices:
            options.insert(1, (current_value, current_value))
        self.fields["novo_responsavel"].choices = options
        if motivo_choices is None:
            motivo_choices = list(Motivo.objects.order_by("nome").values_list("nome", flat=True))
        motivo_options = [("", "Selecione um motivo")] + [(motivo, motivo) for motivo in motivo_choices]
        current_motivo = self.initial.get("motivo")
        if current_motivo and current_motivo not in motivo_choices:
            motivo_options.insert(1, (current_motivo, current_motivo))
        self.fields["motivo"].choices = motivo_options
        razoes = razao_choices or []
        razao_options = [("", "Selecione uma razão")] + [(valor, valor) for valor in razoes]
        current_razao = self.initial.get("razao")
        if current_razao and current_razao not in razoes:
            razao_options.insert(1, (current_razao, current_razao))
        self.fields["razao"].choices = razao_options


class ExitForm(BootstrapFormMixin, forms.Form):
    data = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Data da saída",
    )
    motivo_saida = forms.CharField(label="Motivo da saída")
    razao_saida = forms.ChoiceField(label="Razão da saída", choices=[])

    def __init__(self, *args, **kwargs):
        razao_choices = kwargs.pop("razao_choices", None)
        super().__init__(*args, **kwargs)
        self.fields["motivo_saida"].widget.attrs.setdefault("list", "lista-motivos-saida")
        razoes = razao_choices or []
        options = [("", "Selecione uma razão")] + [(valor, valor) for valor in razoes]
        current = self.initial.get("razao_saida")
        if current and current not in razoes:
            options.insert(1, (current, current))
        self.fields["razao_saida"].choices = options


class ImportClientsForm(BootstrapFormMixin, forms.Form):
    arquivo = forms.FileField(
        label="Arquivo XLSX",
        help_text="Envie um arquivo .xlsx com as colunas CLIENTE, TERMÔMETRO, RESPONSÁVEL, STATUS, ENTRADA, SAÍDA, VALOR, PERMUTA, MOTIVO e RAZÃO.",
        validators=[FileExtensionValidator(allowed_extensions=["xlsx"])],
    )


class ImportMotivosRazoesForm(BootstrapFormMixin, forms.Form):
    arquivo = forms.FileField(
        label="Arquivo XLSX",
        help_text="Planilha .xlsx com colunas: MOTIVO e, opcionalmente, RAZAO e TIPO (transferencia, alteracao_de_valor, registro_de_saida, alteracao_de_termometro).",
        validators=[FileExtensionValidator(allowed_extensions=["xlsx"])],
    )


class ImportResponsaveisForm(BootstrapFormMixin, forms.Form):
    arquivo = forms.FileField(
        label="Arquivo XLSX",
        help_text="Planilha .xlsx com colunas NOME (obrigatório), EMAIL e ATIVO (SIM/NÃO).",
        validators=[FileExtensionValidator(allowed_extensions=["xlsx"])],
    )


class ResponsavelForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Responsavel
        fields = ["nome", "email", "ativo"]


class ConsultorForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Consultor
        fields = ["nome", "email", "ativo"]


class MotivoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Motivo
        fields = ["nome"]


class RazaoForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Razao
        fields = ["nome", "motivo", "tipo_de_historico"]


class TermometroChangeForm(BootstrapFormMixin, forms.Form):
    novo_termometro = forms.ChoiceField(label="Novo termômetro", choices=TERMOMETRO_CHOICES)
    data = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Data da alteração",
    )
    motivo = forms.CharField(label="Motivo", max_length=255)
    razao = forms.ChoiceField(label="Razão", choices=[])

    def __init__(self, *args, **kwargs):
        razao_choices = kwargs.pop("razao_choices", None)
        super().__init__(*args, **kwargs)
        self.fields["motivo"].widget.attrs.setdefault("list", "lista-motivos-termometro")
        razoes = razao_choices or []
        options = [("", "Selecione uma razão")] + [(valor, valor) for valor in razoes]
        current = self.initial.get("razao")
        if current and current not in razoes:
            options.insert(1, (current, current))
        self.fields["razao"].choices = options


class ReuniaoPreferenciaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ReuniaoPreferencia
        fields = [
            "dia_pref_inicio",
            "dia_pref_fim",
            "dia_semana_pref",
            "horario_pref",
            "local",
            "local_descricao",
            "duracao_minutos",
            "data_sugerida",
            "observacoes",
            "consultor",
        ]
        widgets = {
            "dia_pref_inicio": forms.NumberInput(attrs={"min": 1, "max": 31, "step": 1, "maxlength": 2}),
            "dia_pref_fim": forms.NumberInput(attrs={"min": 1, "max": 31, "step": 1, "maxlength": 2}),
            "data_sugerida": forms.NumberInput(attrs={"min": 1, "max": 31, "step": 1, "maxlength": 2}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop("client")
        self.tipo = kwargs.pop("tipo")
        self.require_alignment = kwargs.pop("require_alignment", False)
        super().__init__(*args, **kwargs)
        numeric_fields = ("dia_pref_inicio", "dia_pref_fim", "data_sugerida")
        for key in numeric_fields:
            if key in self.fields:
                self.fields[key].widget.attrs.setdefault("inputmode", "numeric")
                self.fields[key].widget.attrs.setdefault("pattern", "[0-9]*")
        if "dia_pref_inicio" in self.fields:
            self.fields["dia_pref_inicio"].label = "Dia inicial"
        if "dia_pref_fim" in self.fields:
            self.fields["dia_pref_fim"].label = "Dia final"
        if "dia_semana_pref" in self.fields:
            self.fields["dia_semana_pref"].label = "Preferência dia da semana"
        if "data_sugerida" in self.fields:
            self.fields["data_sugerida"].label = "Dia sugerido (número)"
        if "observacoes" in self.fields:
            self.fields["observacoes"].label = "Observações"
        self.fields["consultor"].queryset = Consultor.objects.filter(ativo=True).order_by("nome")
        if self.tipo == "ALINHAMENTO":
            # No consultor selection for alinhamento, it's tied to o responsável do cliente.
            self.fields["consultor"].required = False
            self.fields["consultor"].widget = forms.HiddenInput()
            if self.client.quer_alinhamento:
                for key in ("horario_pref", "local", "duracao_minutos"):
                    if key in self.fields:
                        self.fields[key].required = True
                if "dia_pref_inicio" in self.fields:
                    self.fields["dia_pref_inicio"].required = True
        else:
            # Fechamento exige consultor.
            self.fields["consultor"].required = True

        accent = "#311E5C" if self.tipo == "ALINHAMENTO" else "#0f766e"
        range_class = (
            f"w-20 rounded-lg border border-gray-200 bg-white px-3 py-2 text-center text-sm "
            f"focus:border-[{accent}] focus:ring-2 focus:ring-[{accent}]/20"
        )
        base_class = (
            f"w-full rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm "
            f"focus:border-[{accent}] focus:ring-2 focus:ring-[{accent}]/20"
        )
        narrow_class = (
            f"w-24 rounded-lg border border-gray-200 bg-white px-3 py-2 text-center text-sm "
            f"focus:border-[{accent}] focus:ring-2 focus:ring-[{accent}]/20"
        )

        def set_attrs(field_name: str, attrs: dict[str, str]) -> None:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update(attrs)

        set_attrs(
            "dia_pref_inicio",
            {"class": range_class, "placeholder": "Início", "data-range-start": "true"},
        )
        set_attrs(
            "dia_pref_fim",
            {"class": range_class, "placeholder": "Fim", "data-range-end": "true"},
        )
        set_attrs("dia_semana_pref", {"class": base_class})
        set_attrs("horario_pref", {"class": base_class})
        set_attrs("local", {"class": base_class})
        set_attrs(
            "local_descricao",
            {"class": base_class, "placeholder": "Link, endereço ou observação"},
        )
        set_attrs("duracao_minutos", {"class": base_class, "placeholder": "Ex.: 30"})
        set_attrs("data_sugerida", {"class": narrow_class, "placeholder": "Dia"})
        set_attrs(
            "observacoes",
            {"class": base_class, "placeholder": "Detalhes adicionais ou restrições"},
        )
        if not isinstance(self.fields["consultor"].widget, forms.HiddenInput):
            set_attrs("consultor", {"class": base_class})

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("dia_pref_inicio")
        end = cleaned.get("dia_pref_fim")
        if start and end and start >= end:
            self.add_error("dia_pref_fim", "Dia final deve ser maior que o inicial.")
        duracao = cleaned.get("duracao_minutos")
        if duracao is not None and duracao <= 0:
            self.add_error("duracao_minutos", "A duração deve ser maior que zero.")
        if self.tipo == "FECHAMENTO":
            consultor = cleaned.get("consultor")
            if not consultor:
                self.add_error("consultor", "Selecione um consultor responsável pelo fechamento.")
            if self.require_alignment:
                raise ValidationError("Cadastre a preferência de alinhamento antes de salvar o fechamento.")
        return cleaned


class ValorChangeForm(BootstrapFormMixin, forms.Form):
    valor = forms.DecimalField(label="Novo valor (R$)", max_digits=10, decimal_places=2)
    permuta = forms.BooleanField(label="Cliente em permuta", required=False)
    data = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Data da alteração",
    )
    motivo = forms.CharField(label="Motivo", max_length=255)
    razao = forms.ChoiceField(label="Razão", choices=[])

    def clean_permuta(self) -> bool:
        return bool(self.cleaned_data.get("permuta"))

    def clean(self):
        cleaned = super().clean()
        permuta = cleaned.get("permuta")
        valor = cleaned.get("valor")
        if permuta:
            cleaned["valor"] = Decimal("0")
        elif valor is None or valor <= 0:
            self.add_error("valor", "Informe um valor maior que zero para clientes sem permuta.")
        return cleaned

    def __init__(self, *args, **kwargs):
        razao_choices = kwargs.pop("razao_choices", None)
        super().__init__(*args, **kwargs)
        self.fields["motivo"].widget.attrs.setdefault("list", "lista-motivos-valor")
        razoes = razao_choices or []
        options = [("", "Selecione uma razão")] + [(valor, valor) for valor in razoes]
        current = self.initial.get("razao")
        if current and current not in razoes:
            options.insert(1, (current, current))
        self.fields["razao"].choices = options
