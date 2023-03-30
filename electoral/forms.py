from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import (
    Usuario, Dirigente, 
    Beneficio, Operativo, PartidoPolitico, 
    Votante, Residencia, Corregimiento,
    AsistenciaIndividual, AsistenciaColectiva)

class CustomCreationForm(UserCreationForm):
    
    class Meta:
        model = Usuario
        fields = '__all__'
        
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }

class BeneficioForm(forms.ModelForm):
    cantidad = forms.IntegerField(min_value=0, required=True)
    class Meta:
        model = Beneficio
        fields = ['nombre', 'cantidad', 'tipo']
        widgets = {
            'tipo': forms.RadioSelect()
        }
        
class OperativoForm(forms.ModelForm):
    fecha = forms.DateTimeField(
        label='Fecha',
        widget=forms.DateInput(attrs={
            'type': 'datetime-local',
        }, format='%Y-%m-%dT%H:%M')
    )

    beneficios = forms.ModelMultipleChoiceField(
        Beneficio.objects.all(),
        help_text='Mantenga presionado "Control" o "Comando" en una Mac, para seleccionar más de uno.',
        required=False
    )
    
    class Meta:
        model = Operativo
        fields = ['titulo', 'direccion', 'fecha', 'beneficios']
        
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 2, 'style': 'resize:none;'}), 
        }
               
class PartidoPoliticoForm(forms.ModelForm):
        
    class Meta:
        model = PartidoPolitico
        fields = ['nombre']

class DirigenteForm(forms.ModelForm):

    class Meta:
        model = Dirigente
        fields = '__all__'

class VotanteForm(forms.ModelForm):
    fecha_nacimiento = forms.DateField(
        label='Fecha de Nacimiento',
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
        }, format='%Y-%m-%m')
    )
    
    class Meta:
        model = Votante
        fields = ['nombre','cedula','fecha_nacimiento','sexo','telefono','dirigente','centro_votacion','mesa','partido_politico']

class ResidenciaForm(forms.ModelForm):

    votantes =  forms.ModelMultipleChoiceField(label='Residentes',
        queryset=Votante.objects.filter(bloqueado=False),
        required=False,
        widget=FilteredSelectMultiple('',is_stacked=False))#,attrs={}))
    
    class Media:
        css = {'all': ('admin/css/widgets.css',)}
        js = [
            "admin/js/core.js",
            "admin/js/SelectBox.js",
            "admin/js/SelectFilter2.js",
        ]
    
    class Meta:
        model = Residencia
        fields = ('__all__')
        
class CorregimientoForm(forms.ModelForm):

    residencias =  forms.ModelMultipleChoiceField(label='Residencias',
        queryset=Residencia.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('',is_stacked=False))#,attrs={}))

    votantes =  forms.ModelMultipleChoiceField(label='Votantes',
        queryset=Votante.objects.filter(bloqueado=False),
        required=False,
        widget=FilteredSelectMultiple('',is_stacked=False))#,attrs={}))
    
    class Media:
        css = {'all': ('admin/css/widgets.css',)}
        js = [
            "admin/js/core.js",
            "admin/js/SelectBox.js",
            "admin/js/SelectFilter2.js",
        ]
    
    class Meta:
        model = Corregimiento
        fields = ('__all__')

# class CandidatoForm(forms.ModelForm):

#     votantes =  forms.ModelMultipleChoiceField(label='Votantes',
#         queryset=Votante.objects.filter(bloqueado=False),
#         required=False,
#         widget=FilteredSelectMultiple('',is_stacked=False))#,attrs={}))
    
#     class Media:
#         css = {'all': ('admin/css/widgets.css',)}
#         js = [
#             "admin/js/core.js",
#             "admin/js/SelectBox.js",
#             "admin/js/SelectFilter2.js",
#         ]
    
#     class Meta:
#         model = Candidato
#         fields = ('__all__')

class AsistenciaIndividualForm(forms.ModelForm):

    class Meta:
        model = AsistenciaIndividual
        fields = '__all__'
        
class AsistenciaColectivaForm(forms.ModelForm):

    class Meta:
        model = AsistenciaColectiva
        fields = '__all__'
    
    