from django.urls import path
from . import views

urlpatterns = [
    #2 LOGIN URLS
    path('registro/', views.registro, name="registro"),
    
    #2 OPCIONES
    path('opciones/', views.opciones, name="opciones"),
    
    #2 INICIO
    path('', views.inicio, name="inicio"),
    path('validar/votante/<cedula>', views.validar_votante, name="validar_votante"),
    path('limitar/votantes/', views.limitar_votantes, name="limitar_votantes"),
    path('desbloquear/votantes/', views.desbloquear_votantes, name="desbloquear_votantes"),
    
    #2 OPERATIVOS
    path('operativos/', views.listar_operativos, name="operativos"),
    path('operativos/agendar/', views.agendar_operativo, name="agendar_operativo"),
    path('operativos/administrar/<id>/', views.administrar_operativo, name="administrar_operativo"),
    path('operativos/eliminar/<id>/', views.eliminar_operativo, name="eliminar_operativo"),
    path('operativos/datatable/asistencias/<id>', views.datatable_asistencias, name="datatable_asistencias"),
    
    #2 VOTANTES URLS
    path('votantes/', views.listar_votantes, name="votantes"),
    path('votantes/agregar/', views.agregar_votante, name="agregar_votante"),
    path('votantes/editar/<id>/', views.editar_votante, name="editar_votante"),
    path('votantes/eliminar/<id>/', views.eliminar_votante, name="eliminar_votante"),
    path('votantes/datatable', views.datatable_votantes, name="datatable_votantes"),
    
    #2 RESIDENCIAS URLS
    path('residencias/', views.listar_residencias, name="residencias"),
    path('residencias/agregar/', views.agregar_residencia, name="agregar_residencia"),
    path('residencias/editar/<id>/', views.editar_residencia, name="editar_residencia"),
    path('residencias/eliminar/<id>/', views.eliminar_residencia, name="eliminar_residencia"),
    path('residencias/datatable', views.datatable_residencias, name="datatable_residencias"), 
       
    #2 CORREGIMIENTOS URLS
    path('corregimientos/', views.listar_corregimientos, name="corregimientos"),
    path('corregimientos/agregar/', views.agregar_corregimiento, name="agregar_corregimiento"),
    path('corregimientos/editar/<id>/', views.editar_corregimiento, name="editar_corregimiento"),
    path('corregimientos/eliminar/<id>/', views.eliminar_corregimiento, name="eliminar_corregimiento"),
    path('corregimientos/datatable', views.datatable_corregimientos, name="datatable_corregimientos"), 
    
    #2 DIRIGENTES URLS
    path('dirigentes/', views.listar_dirigentes, name="dirigentes"),
    path('dirigentes/agregar/', views.agregar_dirigente, name="agregar_dirigente"),
    path('dirigentes/editar/<id>/', views.editar_dirigente, name="editar_dirigente"),
    path('dirigentes/eliminar/<id>/', views.eliminar_dirigente, name="eliminar_dirigente"),
    path('dirigentes/datatable', views.datatable_dirigentes, name="datatable_dirigentes"),
    
    #2 INVENTARIO URLS
    path('inventario/beneficios/', views.listar_beneficios, name="beneficios"),
    path('inventario/beneficios/agregar/', views.agregar_beneficio, name="agregar_beneficio"),
    path('inventario/beneficios/editar/<id>/', views.editar_beneficio, name="editar_beneficio"),
    path('inventario/beneficios/eliminar/<id>/', views.eliminar_beneficio, name="eliminar_beneficio"),
    path('inventario/beneficios/datatable', views.datatable_beneficios, name="datatable_beneficios"),
]