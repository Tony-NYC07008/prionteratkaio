from django.contrib import admin
from .models import User, Shift, PaperRefill, PaperOrder, History

# Registrierung der Modelle im Admin-Interface
admin.site.register(User)
admin.site.register(Shift)
admin.site.register(PaperRefill)
admin.site.register(PaperOrder)
admin.site.register(History)
