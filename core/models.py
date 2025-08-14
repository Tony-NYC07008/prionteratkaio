from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Eigenes User-Modell mit Rollen
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.username} ({self.role})"

# Modell für Schichten
class Shift(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)  # jetzt optional
    end_time = models.TimeField(null=True, blank=True)    # jetzt optional
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.date} - {self.description or 'Keine Beschreibung'}"

# Modell für Papiernachfüllung
class PaperRefill(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)  # Welche Schicht hat nachgefüllt
    date = models.DateTimeField(auto_now_add=True)  # Nachfüllzeitpunkt
    amount = models.PositiveIntegerField()  # Menge Papier nachgefüllt
    confirmed = models.BooleanField(default=False)  # Bestätigung, dass Papier nachgefüllt wurde

    def __str__(self):
        return f"Nachfüllung am {self.date} - Menge: {self.amount}"

# Modell für Papierbestellungen
class PaperOrder(models.Model):
    order_date = models.DateTimeField(auto_now_add=True)  # Bestelldatum
    amount = models.PositiveIntegerField()  # Bestellmenge
    delivered = models.BooleanField(default=False)  # Lieferung eingetroffen?
    delivered_date = models.DateTimeField(null=True, blank=True)  # Lieferdatum (optional)

    def __str__(self):
        return f"Bestellung vom {self.order_date} - Menge: {self.amount} - Geliefert: {self.delivered}"

# Modell für Aktionen-Historie
class History(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)  # Beschreibung der Aktion
    timestamp = models.DateTimeField(auto_now_add=True)  # Zeitstempel der Aktion

    def __str__(self):
        return f"{self.user} - {self.action} am {self.timestamp}"
