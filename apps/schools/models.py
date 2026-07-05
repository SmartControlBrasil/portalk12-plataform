from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class SchoolStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Ativa"
    INACTIVE = "INACTIVE", "Inativa"
    SUSPENDED = "SUSPENDED", "Suspensa"


class School(models.Model):
    name = models.CharField("nome da escola", max_length=180)
    slug = models.SlugField("slug", max_length=220, unique=True, blank=True)

    legal_name = models.CharField("razão social", max_length=180, blank=True)
    document = models.CharField("CNPJ/CPF", max_length=32, blank=True)

    email = models.EmailField("e-mail", blank=True)
    phone = models.CharField("telefone", max_length=32, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=32, blank=True)

    director = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="diretor responsável",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="directed_schools",
    )

    zip_code = models.CharField("CEP", max_length=16, blank=True)
    address = models.CharField("endereço", max_length=220, blank=True)
    number = models.CharField("número", max_length=20, blank=True)
    complement = models.CharField("complemento", max_length=120, blank=True)
    district = models.CharField("bairro", max_length=120, blank=True)
    city = models.CharField("cidade", max_length=120, blank=True)
    state = models.CharField("UF", max_length=2, blank=True)

    status = models.CharField(
        "status",
        max_length=20,
        choices=SchoolStatus.choices,
        default=SchoolStatus.ACTIVE,
    )

    notes = models.TextField("observações", blank=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "escola"
        verbose_name_plural = "escolas"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "escola"
            slug = base_slug
            counter = 1

            while School.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"

            self.slug = slug

        super().save(*args, **kwargs)