from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    """Adds created/updated fields to key tables for auditing."""

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Responsavel(TimeStampedModel):
    nome = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class Motivo(TimeStampedModel):
    nome = models.CharField(max_length=150, unique=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class Razao(TimeStampedModel):
    TIPO_HISTORICO_CHOICES = [
        ("transferencia", "Transferência"),
        ("alteracao_de_valor", "Alteração de valor"),
        ("registro_de_saida", "Registro de saída"),
        ("alteracao_de_termometro", "Alteração de termômetro"),
    ]

    nome = models.CharField(max_length=150)
    motivo = models.ForeignKey(Motivo, related_name="razoes", on_delete=models.CASCADE)
    tipo_de_historico = models.CharField(max_length=30, choices=TIPO_HISTORICO_CHOICES)

    class Meta:
        ordering = ["nome"]
        unique_together = ("nome", "tipo_de_historico")

    def __str__(self) -> str:
        return f"{self.nome} ({self.get_tipo_de_historico_display()})"


class Client(TimeStampedModel):
    STATUS_CHOICES = [("ATIVO", "Ativo"), ("INATIVO", "Inativo")]

    nome = models.CharField(max_length=255)
    termometro = models.PositiveSmallIntegerField(default=3)
    responsavel = models.CharField(max_length=100)
    quer_alinhamento = models.BooleanField(default=False)
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default="ATIVO")
    entrada = models.DateField()
    saida = models.DateField(null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    permuta = models.BooleanField(default=False)
    motivo = models.CharField(max_length=255, blank=True)
    razao = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-entrada", "nome"]

    def __str__(self) -> str:
        return f"{self.nome} ({self.responsavel})"


class Consultor(TimeStampedModel):
    nome = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class ReuniaoPreferencia(TimeStampedModel):
    TIPOS = [("ALINHAMENTO", "Alinhamento"), ("FECHAMENTO", "Fechamento")]
    HORARIO_CHOICES = [
        ("MANHA", "Manhã"),
        ("TARDE", "Tarde"),
        ("NOITE", "Noite"),
    ]
    LOCAL_CHOICES = [
        ("ESCRITORIO", "Escritório"),
        ("ONLINE", "Reunião Online"),
        ("CLIENTE", "No cliente"),
        ("OUTRO", "Outro"),
    ]
    DIA_SEMANA_CHOICES = [
        ("SEGUNDA", "Segunda-feira"),
        ("TERCA", "Terça-feira"),
        ("QUARTA", "Quarta-feira"),
        ("QUINTA", "Quinta-feira"),
        ("SEXTA", "Sexta-feira"),
    ]

    client = models.ForeignKey(Client, related_name="preferencias_reuniao", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=15, choices=TIPOS)
    dia_pref_inicio = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
    )
    dia_pref_fim = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
    )
    dia_semana_pref = models.CharField(max_length=15, choices=DIA_SEMANA_CHOICES, blank=True)
    horario_pref = models.CharField(max_length=30, choices=HORARIO_CHOICES, blank=True)
    local = models.CharField(max_length=30, choices=LOCAL_CHOICES, blank=True)
    local_descricao = models.CharField(max_length=255, blank=True)
    duracao_minutos = models.PositiveSmallIntegerField(null=True, blank=True)
    data_sugerida = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(31)],
    )
    observacoes = models.TextField(blank=True)
    responsavel_nome = models.CharField(max_length=100, blank=True)
    consultor = models.ForeignKey(
        Consultor,
        related_name="reunioes",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        unique_together = ("client", "tipo")
        ordering = ["client__nome", "tipo"]

    def __str__(self) -> str:
        return f"{self.client.nome} - {self.get_tipo_display()}"


class ClientHistory(TimeStampedModel):
    TIPOS = [
        ("TRANSFERENCIA", "Transferência"),
        ("SAIDA", "Saída"),
        ("TERMOMETRO", "Termômetro"),
        ("VALOR", "Valor/Permuta"),
    ]

    client = models.ForeignKey(Client, related_name="historico", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    data = models.DateField()
    motivo = models.CharField(max_length=255)
    razao = models.CharField(max_length=255, blank=True)
    responsavel_antigo = models.CharField(max_length=100, blank=True)
    responsavel_novo = models.CharField(max_length=100, blank=True)
    status_antigo = models.CharField(max_length=7, blank=True)
    status_novo = models.CharField(max_length=7, blank=True)
    termometro_antigo = models.PositiveSmallIntegerField(null=True, blank=True)
    termometro_novo = models.PositiveSmallIntegerField(null=True, blank=True)
    valor_antigo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valor_novo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    permuta_antiga = models.BooleanField(null=True, blank=True)
    permuta_nova = models.BooleanField(null=True, blank=True)

    class Meta:
        ordering = ["-data"]

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} - {self.client.nome} ({self.data:%d/%m/%Y})"

    @property
    def descricao_alteracao(self) -> str:
        def _format_permuta(value: bool | None) -> str:
            if value is None:
                return "—"
            return "Sim" if value else "Não"

        if self.tipo == "TRANSFERENCIA" and (self.responsavel_antigo or self.responsavel_novo):
            return f"Responsável: {self.responsavel_antigo or '-'} → {self.responsavel_novo or '-'}"
        if self.tipo == "SAIDA" and (self.status_antigo or self.status_novo):
            return f"Status: {self.status_antigo or '-'} → {self.status_novo or '-'}"
        if self.tipo == "TERMOMETRO" and (self.termometro_antigo or self.termometro_novo):
            return f"Termômetro: {self.termometro_antigo or '-'} → {self.termometro_novo or '-'}"
        if self.tipo == "VALOR":
            detalhes = []
            if self.valor_antigo is not None or self.valor_novo is not None:
                valor_ant = f"R$ {self.valor_antigo:.2f}" if self.valor_antigo is not None else "—"
                valor_novo = f"R$ {self.valor_novo:.2f}" if self.valor_novo is not None else "—"
                detalhes.append(f"Valor: {valor_ant} → {valor_novo}")
            if self.permuta_antiga is not None or self.permuta_nova is not None:
                detalhes.append(
                    f"Permuta: {_format_permuta(self.permuta_antiga)} → {_format_permuta(self.permuta_nova)}"
                )
            return " · ".join(detalhes) or "Valor ajustado"

        return ""


class AgendamentoAlinhamento(TimeStampedModel):
    STATUS_CHOICES = [
        ("PENDENTE", "Pendente"),
        ("AGENDADO", "Agendado"),
        ("REALIZADO", "Realizado"),
        ("CANCELADO", "Cancelado"),
    ]

    client = models.ForeignKey(Client, related_name="agendamentos_alinhamento", on_delete=models.CASCADE)
    mes = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    ano = models.PositiveSmallIntegerField()
    data_reuniao = models.DateField(null=True, blank=True)
    horario = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDENTE")
    observacao = models.TextField(blank=True)

    class Meta:
        unique_together = ("client", "mes", "ano")
        ordering = ["data_reuniao", "client__nome"]

    def __str__(self) -> str:
        return f"Alinhamento - {self.client.nome} - {self.mes}/{self.ano}"


class AgendamentoFechamento(TimeStampedModel):
    STATUS_CHOICES = [
        ("PENDENTE", "Pendente"),
        ("AGENDADO", "Agendado"),
        ("REALIZADO", "Realizado"),
        ("CANCELADO", "Cancelado"),
    ]

    client = models.ForeignKey(Client, related_name="agendamentos_fechamento", on_delete=models.CASCADE)
    mes = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    ano = models.PositiveSmallIntegerField()
    data_reuniao = models.DateField(null=True, blank=True)
    horario = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDENTE")
    observacao = models.TextField(blank=True)

    class Meta:
        unique_together = ("client", "mes", "ano")
        ordering = ["data_reuniao", "client__nome"]

    def __str__(self) -> str:
        return f"Fechamento - {self.client.nome} - {self.mes}/{self.ano}"
