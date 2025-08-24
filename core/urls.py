from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('my_shifts/', views.my_shifts_view, name='my_shifts'),
    path('manage_shifts/', views.manage_shifts, name='manage_shifts'),
    path('add_shift/', views.add_shift, name='add_shift'),
    path('edit_shift/', views.edit_shift, name='edit_shift'),
    path('edit_shift_form/', views.edit_shift_form, name='edit_shift_form'),
    path("delete_shift/", views.delete_shift, name="delete_shift"),
    path("delete_shift_confirm/<int:pk>/", views.delete_shift_confirm, name="delete_shift_confirm"),

    path('list_users/', views.list_users_view, name='list_users'),

    path('calendar/', views.calendar_view, name='calendar'),
    path('api/shifts/', views.shifts_json, name='shifts_json'),
    path('shifts_json/', views.shifts_json, name='shifts_json'),

    # WICHTIG: hier auf die richtigen Views zeigen

    path('delete_user/', views.delete_user_view, name='delete_user'),

    path('papier-nachfuellen/', views.papier_nachfuellen, name='papier_nachfuellen'),
]
