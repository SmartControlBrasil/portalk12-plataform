from django.db import models

# Create your models here.
from decimal import Decimal

from django.conf import settings
from django.db import models


class CantinaProductStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Ativo"
    INACTIVE = "INACTIVE", "Inativo"
    OUT_OF_STOCK = "OUT_OF_STOCK", "Sem estoque"


class CantinaOrderStatus(models.TextChoices):
    DRAFT = "DRAFT", "Rascunho"
    PENDING = "PENDING", "Pendente"
    PAID = "PAID", "Pago"
    DELIVERED = "DELIVERED", "Entregue"
    CANCELLED = "CANCELLED", "Cancelado"


class CantinaPaymentMethod(models.TextChoices):
    CASH = "CASH", "Dinheiro"
    PIX = "PIX", "Pix"
    CARD = "CARD", "Cartão"
    SCHOOL_CREDIT = "SCHOOL_CREDIT", "Crédito escolar"
    OTHER = "OTHER", "Outro"


class CantinaProductCategory(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="cantina_product_categories",
    )

    name = models.CharField("nome", max_length=120)
    description = models.TextField("descrição", blank=True)

    is_active = models.BooleanField("ativa", default=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "categoria de produto da cantina"
        verbose_name_plural = "categorias de produtos da cantina"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_cantina_category_name_per_school",
            ),
        ]

    def __str__(self):
        return f"{self.school.name} - {self.name}"


class CantinaProduct(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="cantina_products",
    )

    category = models.ForeignKey(
        CantinaProductCategory,
        verbose_name="categoria",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    name = models.CharField("nome", max_length=160)
    description = models.TextField("descrição", blank=True)

    sku = models.CharField("código/SKU", max_length=60, blank=True)

    price = models.DecimalField(
        "preço",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    cost_price = models.DecimalField(
        "custo",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    current_stock = models.DecimalField(
        "estoque atual",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    minimum_stock = models.DecimalField(
        "estoque mínimo",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    unit = models.CharField(
        "unidade",
        max_length=30,
        default="un",
        help_text="Exemplo: un, kg, pacote, copo.",
    )

    image = models.ImageField(
        "imagem",
        upload_to="cantina/products/",
        null=True,
        blank=True,
    )

    status = models.CharField(
        "status",
        max_length=20,
        choices=CantinaProductStatus.choices,
        default=CantinaProductStatus.ACTIVE,
    )

    is_restricted = models.BooleanField(
        "produto restrito",
        default=False,
        help_text="Use para produtos que exigem controle da escola ou autorização do responsável.",
    )

    notes = models.TextField("observações", blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_cantina_products",
    )

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "produto da cantina"
        verbose_name_plural = "produtos da cantina"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "sku"],
                name="unique_cantina_product_sku_per_school",
                condition=~models.Q(sku=""),
            ),
            models.UniqueConstraint(
                fields=["school", "name"],
                name="unique_cantina_product_name_per_school",
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock

    @property
    def is_available(self):
        return (
            self.status == CantinaProductStatus.ACTIVE
            and self.current_stock > 0
        )


class CantinaOrder(models.Model):
    school = models.ForeignKey(
        "schools.School",
        verbose_name="escola",
        on_delete=models.CASCADE,
        related_name="cantina_orders",
    )

    student = models.ForeignKey(
        "students.Student",
        verbose_name="aluno",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cantina_orders",
    )

    responsible_guardian = models.ForeignKey(
        "students.StudentGuardian",
        verbose_name="responsável",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cantina_orders",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="criado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_cantina_orders",
    )

    status = models.CharField(
        "status",
        max_length=20,
        choices=CantinaOrderStatus.choices,
        default=CantinaOrderStatus.PENDING,
    )

    payment_method = models.CharField(
        "forma de pagamento",
        max_length=30,
        choices=CantinaPaymentMethod.choices,
        default=CantinaPaymentMethod.OTHER,
    )

    paid_at = models.DateTimeField("pago em", null=True, blank=True)
    delivered_at = models.DateTimeField("entregue em", null=True, blank=True)

    notes = models.TextField("observações", blank=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "pedido da cantina"
        verbose_name_plural = "pedidos da cantina"
        ordering = ["-created_at"]

    def __str__(self):
        student_name = self.student.display_name if self.student else "sem aluno"
        return f"Pedido #{self.pk} - {student_name}"

    @property
    def total_amount(self):
        return sum(item.total_amount for item in self.items.all())


class CantinaOrderItem(models.Model):
    order = models.ForeignKey(
        CantinaOrder,
        verbose_name="pedido",
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        CantinaProduct,
        verbose_name="produto",
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    quantity = models.DecimalField(
        "quantidade",
        max_digits=10,
        decimal_places=2,
        default=Decimal("1.00"),
    )

    unit_price = models.DecimalField(
        "preço unitário",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    notes = models.TextField("observações", blank=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "item do pedido da cantina"
        verbose_name_plural = "itens dos pedidos da cantina"
        ordering = ["product__name"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_amount(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        if self.product and self.unit_price == Decimal("0.00"):
            self.unit_price = self.product.price

        super().save(*args, **kwargs)