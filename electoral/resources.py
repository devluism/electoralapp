from django.contrib.auth import hashers
from django.contrib import admin
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin

from .forms import ResidenciaForm, CorregimientoForm

from .models import (
    CentroVotacion, Mesa, 
    Usuario, Dirigente, 
    Beneficio,Operativo, PartidoPolitico, 
    Votante, Residencia, Corregimiento,
    AsistenciaIndividual, AsistenciaColectiva)

class CentroVotacionResource(resources.ModelResource):
    
    class Meta:
        model = CentroVotacion
        
class CentroVotacionAdmin(ImportExportModelAdmin):
    resource_class = CentroVotacionResource

# class MesaResource(resources.ModelResource):

#     class Meta:
#         model = Mesa
        
# class MesaAdmin(ImportExportModelAdmin):
#     resource_class = MesaResource

class UserResource(resources.ModelResource):
    
    # def before_import_row(self, row, **kwargs):
    #     try:
    #         row['password'] = hashers.make_password(password=row['password'])
            
    #     except Exception as e:
    #         print(e)
    
    class Meta:
        model = Usuario
        fields = ('id', 'nombre', 'cedula', 'telefono', 'password', 'barrio', 'sector', 'direccion', 'fecha_nacimiento', 'edad', 'sexo')

        widgets = {
            'fecha_nacimiento': {'format': '%d/%m/%Y'},
        }
    
class BeneficioResource(resources.ModelResource):

    class Meta:
        model = Beneficio
        fields = ('nombre', 'cantidad', 'tipo')
        
class BeneficioAdmin(ImportExportModelAdmin):
    resource_class = BeneficioResource
 
class OperativoResource(resources.ModelResource):

    class Meta:
        model = Operativo
        fields = ('titulo', 'cede', 'barrio', 'sector', 'direccion', 'fecha', 'beneficios')
        
class OperativoAdmin(ImportExportModelAdmin):
    resource_class = OperativoResource
    
class PartidoPoliticoResource(resources.ModelResource):

    class Meta:
        model = PartidoPolitico
        fields = ('nombre')
        
class PartidoPoliticoAdmin(ImportExportModelAdmin):
    resource_class = PartidoPoliticoResource

class DirigenteResource(resources.ModelResource):

    class Meta:
        model = Dirigente
        import_id_fields = ('cedula',)
        fields = ('nombre','cedula','es_apoyo')
        
class DirigenteAdmin(ImportExportModelAdmin):
    resource_class = DirigenteResource

class VotanteResource(resources.ModelResource):
    
    # dirigente = fields.Field(column_name='dirigente',attribute='dirigente',widget=widgets.ForeignKeyWidget(model=Usuario, field='cedula'))
    # mesa = fields.Field(column_name='mesa',attribute='mesa',widget=widgets.ForeignKeyWidget(model=Mesa, field='codigo'))
    # operativos = fields.Field(column_name='operativos',attribute='operativos',widget=widgets.ManyToManyWidget(model=Operativo, field='id'))
    centro_votacion = fields.Field(column_name='centro_votacion',attribute='centro_votacion',widget=widgets.ForeignKeyWidget(model=CentroVotacion, field='cede'))
    partido_politico = fields.Field(column_name='partido_politico',attribute='partido_politico',widget=widgets.ForeignKeyWidget(model=PartidoPolitico, field='nombre'))
    dirigente = fields.Field(column_name='dirigente',attribute='dirigente',widget=widgets.ForeignKeyWidget(model=Dirigente, field='cedula'))
    
    class Meta:
        model = Votante
        import_id_fields = ('codigo',)
        fields = ('codigo','nombre','cedula','fecha_nacimiento','sexo','telefono','dirigente','centro_votacion','partido_politico')
        
class VotanteAdmin(ImportExportModelAdmin):
    resource_class = VotanteResource
    list_display = ('codigo','nombre','cedula','bloqueado')
    list_editable = ('bloqueado',)
    list_display_links = ('nombre',)
    list_filter = ('bloqueado',)
    search_fields = ('codigo', 'nombre', 'cedula')
    ordering = ('codigo',)

class ResidenciaResource(resources.ModelResource):
    
    votantes = fields.Field(saves_null_values=True,column_name='votantes',attribute='votantes',widget=widgets.ManyToManyWidget(model=Votante, separator=',',field='cedula'))
    
    class Meta:
        model = Residencia
        fields = ('numero_casa','barriada','sector','direccion','votantes')
        
class ResidenciaAdmin(ImportExportModelAdmin):
    resource_class = ResidenciaResource
    form = ResidenciaForm
    
class CorregimientoResource(resources.ModelResource):
    
    residencias = fields.Field(saves_null_values=True,column_name='residencias',attribute='residencias',widget=widgets.ManyToManyWidget(model=Residencia, separator=',',field='id'))
    votantes = fields.Field(saves_null_values=True,column_name='votantes',attribute='votantes',widget=widgets.ManyToManyWidget(model=Residencia, separator=',',field='cedula'))

    class Meta:
        model = Corregimiento
        fields = ('nombre','residencias','votantes')
        
class CorregimientoAdmin(ImportExportModelAdmin):
    resource_class = CorregimientoResource
    form = CorregimientoForm
   
class AsistenciaIndividualResource(resources.ModelResource):
    
    votante = fields.Field(column_name='votante',attribute='votante',widget=widgets.ForeignKeyWidget(model=Votante, field='cedula'))
    operativo = fields.Field(column_name='operativo',attribute='operativo',widget=widgets.ForeignKeyWidget(model=Operativo, field='id'))

    class Meta:
        model = AsistenciaIndividual
        fields = ('votante','operativo','beneficios','fecha')

class AsistenciaIndividualAdmin(ImportExportModelAdmin):
    resource_class = AsistenciaIndividualResource
    
class AsistenciaColectivaResource(resources.ModelResource):

    class Meta:
        model = AsistenciaColectiva
        fields = ('residencia','operativo','beneficios','fecha')
        
class AsistenciaColectivaAdmin(ImportExportModelAdmin):
    resource_class = AsistenciaColectivaResource
    

        