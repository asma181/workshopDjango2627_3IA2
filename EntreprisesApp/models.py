
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import DecimalField
from django.core.exceptions import ValidationError
import re


def validate_gmail(value):
    if not value.lower().endswith("@gmail.com"):
        raise ValidationError("Seuls les emails gmail.com sont acceptés.")


def validate_matricule_fiscale(value):
    pattern = r"^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$"
    if not re.fullmatch(pattern, value):
        raise ValidationError("Matricule fiscal invalide.")


def validate_adresse(value):
    if len(value.strip()) < 20:
        raise ValidationError("L'adresse doit contenir au minimum 20 caractères.")


class Utilsateur(AbstractUser):
    user_id = models.CharField(max_length=8, editable=False, primary_key=True)
    email = models.EmailField(unique=True, validators=[validate_gmail])
    role = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'admin'),
            ('transporteur', 'transporteur'),
            ('chargeur', 'chargeur')
        ],
        default='chargeur'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    telephone = models.CharField(max_length=8)


class entreprise(models.Model):
    raison_sociale = models.CharField(max_length=100)
    matricule_fiscale = models.CharField(
        max_length=17,
        unique=True,
        validators=[validate_matricule_fiscale]
    )
    type_entreprise = models.CharField(
        max_length=15,
        choices=[
            ('chargeur', 'chargeur'),
            ('transporteur', 'transporteur')
        ],
        default='chargeur'
    )
    adresse = models.CharField(
        max_length=100,
        validators=[validate_adresse]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
gerant = models.OneToOneField(
    Utilsateur,
    on_delete=models.CASCADE,
    related_name='entreprise'
)
