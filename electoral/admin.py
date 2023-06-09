from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from import_export.admin import ImportExportModelAdmin

from .models import (
    CentroVotacion, 
    Usuario, Dirigente, 
    Beneficio,Operativo, PartidoPolitico, 
    Votante, Residencia, Corregimiento,
    AsistenciaIndividual, AsistenciaColectiva, EventoLog)

from .resources import (
    CentroVotacionAdmin, 
    UserResource, DirigenteAdmin, 
    BeneficioAdmin, OperativoAdmin, PartidoPoliticoAdmin, 
    VotanteAdmin, ResidenciaAdmin, CorregimientoAdmin,
    AsistenciaIndividualAdmin, AsistenciaColectivaAdmin, EventoLogAdmin)

# Register your models here.
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ('cedula', 'telefono')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Usuario
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class UserAdmin(BaseUserAdmin, ImportExportModelAdmin):
    resource_class = UserResource
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id','nombre','cedula','is_admin')
    list_display_links = ('id','nombre',)
    list_filter = ('is_active',)
    fieldsets = (
        ('Datos de Acceso', {'fields': ('cedula','password','is_superuser')}),
        ('Información Personal', {'fields': (
            'nombre',
            'telefono',
        )}),
        ('Permisos y opciones', {'fields': ('is_admin','is_active', 'tema')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nombre','cedula', 'telefono', 'password1', 'password2'),
        }),
    )
    search_fields = ('id', 'nombre', 'cedula')
    ordering = ('id',)
    filter_horizontal = ()

admin.site.register(CentroVotacion, CentroVotacionAdmin)
# admin.site.register(Mesa, MesaAdmin)
admin.site.register(Usuario, UserAdmin)
admin.site.register(Beneficio, BeneficioAdmin)
admin.site.register(Operativo, OperativoAdmin)
admin.site.register(PartidoPolitico, PartidoPoliticoAdmin)
admin.site.register(Dirigente, DirigenteAdmin)
admin.site.register(Votante, VotanteAdmin)
admin.site.register(Residencia, ResidenciaAdmin)
admin.site.register(Corregimiento, CorregimientoAdmin)
admin.site.register(AsistenciaIndividual, AsistenciaIndividualAdmin)
admin.site.register(AsistenciaColectiva, AsistenciaColectivaAdmin)
admin.site.register(EventoLog, EventoLogAdmin)


# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)