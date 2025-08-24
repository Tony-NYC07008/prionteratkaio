from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import EmailMessage
from django.contrib import messages
from django.conf import settings
from datetime import date
from django.contrib.admin.views.decorators import staff_member_required
from .forms import RegistrationForm, ShiftForm
from .models import Shift

User = get_user_model()


# =========================
# Helfer / Decorators
# =========================

def superuser_required(view_func):
    """Kombiniert Login und Superuser-Check"""
    decorated = login_required(user_passes_test(lambda u: u.is_superuser)(view_func))
    return decorated


# =========================
# Auth Views
# =========================

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('my_shifts')
    else:
        form = AuthenticationForm()
    return render(request, 'papiermanager/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# =========================
# Registrierung
# =========================
@superuser_required
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        role = request.POST.get("role", "")

        if not username or not password1 or not password2 or not role:
            messages.error(request, "Bitte alle Felder ausfüllen.")
        elif password1 != password2:
            messages.error(request, "Passwörter stimmen nicht überein.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Benutzername existiert bereits.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Diese E-Mail wird bereits verwendet.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.role = role
            if role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            user.save()
            # Positive Meldung entfernt
            return redirect("my_shifts")

    return render(request, "papiermanager/register.html")



# =========================
# Schichten
# =========================

@login_required
def my_shifts_view(request):
    shifts = Shift.objects.filter(user=request.user).order_by('date', 'start_time')
    return render(request, 'papiermanager/my_shifts.html', {'shifts': shifts})


@login_required
def manage_shifts(request):
    if request.user.is_superuser:
        shifts = Shift.objects.all().order_by("date", "start_time")
    else:
        shifts = Shift.objects.filter(user=request.user).order_by("date", "start_time")
    return render(request, "papiermanager/manage_shifts.html", {"shifts": shifts})


@login_required
def add_shift(request):
    if request.method == "POST":
        form = ShiftForm(request.POST)
        if form.is_valid():
            shift = form.save(commit=False)
            shift.user = request.user
            shift.save()
            messages.success(request, "Schicht erfolgreich hinzugefügt ✅")
            return redirect('my_shifts')
    else:
        form = ShiftForm()
    return render(request, 'papiermanager/add_shift.html', {'form': form})


@login_required
def edit_shift(request):
    if request.user.is_superuser:
        shifts = Shift.objects.all().order_by('date', 'start_time')
    else:
        shifts = Shift.objects.filter(user=request.user).order_by('date', 'start_time')
    return render(request, 'papiermanager/edit_shift.html', {'shifts': shifts})


@login_required
def edit_shift_form(request):
    pk = request.POST.get('shift_pk') or request.GET.get('shift_pk')
    shift = get_object_or_404(Shift, pk=pk)

    if request.method == 'POST' and 'save' in request.POST:
        shift.date = request.POST.get('date')
        shift.description = request.POST.get('description')
        shift.save()
        messages.success(request, "Schicht erfolgreich gespeichert ✅")
        return redirect('edit_shift')

    return render(request, 'papiermanager/edit_shift_form.html', {
        'shift': shift,
    })



@login_required
def delete_shift(request):
    if request.user.is_superuser:
        shifts = Shift.objects.all().order_by("date", "start_time")
    else:
        shifts = Shift.objects.filter(user=request.user).order_by("date", "start_time")
    return render(request, "papiermanager/delete_shift.html", {"shifts": shifts})


@login_required
def delete_shift_confirm(request, pk):
    shift = get_object_or_404(Shift, pk=pk)

    # nur der Besitzer oder Admin darf löschen
    if not request.user.is_superuser and shift.user != request.user:
        messages.error(request, "Keine Berechtigung ❌")
        return redirect("delete_shift")

    if request.method == "POST":
        shift.delete()
        messages.success(request, "Schicht erfolgreich gelöscht ✅")
        return redirect("delete_shift")

    # Falls jemand GET aufruft → direkt zurück
    return redirect("delete_shift")



# =========================
# Benutzerverwaltung
# =========================




@superuser_required
def delete_user_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()

        if not username or not email:
            messages.error(request, "Bitte Benutzername und E-Mail eingeben.")
            return render(request, "papiermanager/delete_user.html")

        try:
            target = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            messages.error(request, "Kein Benutzer mit diesen Daten gefunden.")
            return render(request, "papiermanager/delete_user.html")

        if target == request.user:
            messages.error(request, "Sie können sich nicht selbst löschen.")
            return render(request, "papiermanager/delete_user.html")

        try:
            target.delete()
            # Positive Meldung entfernt
        except Exception as e:
            messages.error(request, f"Fehler beim Löschen des Benutzers: {e}")

        return redirect("my_shifts")

    return render(request, "papiermanager/delete_user.html")


@superuser_required
def list_users_view(request):
    users = User.objects.all().order_by('username')  # Alle User alphabetisch
    return render(request, "papiermanager/list_users.html", {"users": users})
# =========================
# Kalender & Shifts API
# =========================

PALETTE = [
    "#4caf50", "#2196f3", "#ff9800", "#9c27b0", "#f44336",
    "#00bcd4", "#8bc34a", "#e91e63", "#ffc107", "#607d8b"
]


def assign_colors_to_users(usernames):
    names = sorted(set([str(n).strip() for n in usernames if n and str(n).strip()]))
    mapping = {}
    for i, name in enumerate(names):
        mapping[name] = PALETTE[i % len(PALETTE)]
    return mapping


@login_required
def calendar_view(request):
    today = date.today()

    all_usernames = Shift.objects.values_list('user__username', flat=True).distinct()
    all_usernames = [u for u in all_usernames if u and str(u).strip()]
    user_colors = assign_colors_to_users(all_usernames)

    if request.user.is_superuser:
        shifts = Shift.objects.filter(date__year=today.year, date__month=today.month).order_by('date','start_time')
    else:
        shifts = Shift.objects.filter(user=request.user, date__year=today.year, date__month=today.month).order_by('date','start_time')

    return render(request, 'papiermanager/calendar.html', {
        'shifts': shifts,
        'today': today,
        'user_colors': user_colors
    })


@login_required
def shifts_json(request):
    all_usernames = Shift.objects.values_list('user__username', flat=True).distinct()
    all_usernames = [u for u in all_usernames if u and str(u).strip()]
    user_colors = assign_colors_to_users(all_usernames)

    shifts = Shift.objects.all()
    events = []
    for shift in shifts:
        username = (shift.user.username or f"user_{shift.user.id}").strip()
        color = user_colors.get(username, '#cccccc')
        events.append({
            'title': username,
            'start': shift.date.isoformat(),
            'allDay': True,
            'backgroundColor': color,
            'borderColor': color,
            'description': shift.description or '',
            'username': username,
        })
    return JsonResponse(events, safe=False)


# =========================
# Papier nachfüllen
# =========================

@login_required
@require_POST
def papier_nachfuellen(request):
    user = request.user
    benutzername = user.get_full_name() or user.username or f"user_{user.id}"

    # Mail an Lager
    subject_lager = "Papier nachfüllen"
    body_lager = (
        f"Hallo\n\n"
        "Wir haben leider im Lager nicht genügend Papier. "
        "Könnten Sie bitte das nachfüllen?\n\n"
        f"Gruss\n{benutzername}"
    )

    email_lager = EmailMessage(
        subject=subject_lager,
        body=body_lager,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=["testpapier0@gmail.com"],
        reply_to=[user.email] if user.email else None,
    )

    try:
        email_lager.send(fail_silently=False)
    except Exception as e:
        messages.error(request, f"Lager-Mail konnte nicht gesendet werden: {e}")
        return redirect("calendar")

    # Mail an alle Benutzer
    all_users = User.objects.exclude(email="").values_list('email', flat=True)
    subject_all = "Papier wurde nachbestellt"
    body_all = (
        "Hallo zusammen,\n\n"
        "Das Papier wurde soeben nachbestellt.\n\n"
        f"Nachbestellt von: {benutzername}"
    )

    email_all = EmailMessage(
        subject=subject_all,
        body=body_all,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=list(all_users),
    )

    try:
        email_all.send(fail_silently=False)
        messages.success(request, "E-Mail an Lager und an alle Benutzer gesendet ✅")
    except Exception as e:
        messages.error(request, f"Mail an Benutzer konnte nicht gesendet werden: {e}")

    return redirect("calendar")
