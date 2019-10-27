from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from apps.users.models import Profile, UserFilter, NewFilter
from apps.users.forms import ProfileCreationForm, ProfileChangeForm


@admin.register(Profile)
class ProfileAdmin(UserAdmin):
    list_display = ('phone', 'email', 'is_active', 'is_superuser')
    search_fields = ('phone', 'email')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Info', {'fields': ('name', 'phone', 'telegram_id', 'profile_type', 'plan_type', 'comment')}),
        ('Rules', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('expired', 'date_joined', 'last_login')}),
    )
    form = ProfileChangeForm
    add_form = ProfileCreationForm
    add_fieldsets = (
        (None, {'fields': ('name', 'email', 'phone', 'password1', 'password2')}),
    )
    readonly_fields = ('date_joined',)
    ordering = ('-date_joined',)


admin.site.register(UserFilter)
admin.site.register(NewFilter)
admin.site.unregister(Group)
