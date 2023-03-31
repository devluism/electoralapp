import json
from django.http import JsonResponse

from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import (
    CentroVotacion, Usuario, 
    Dirigente, Beneficio, 
    Operativo, Votante, 
    Residencia, Corregimiento, Entrega,
    AsistenciaIndividual, AsistenciaColectiva, EventoLog)

from .forms import (
    CustomCreationForm, BeneficioForm, 
    DirigenteForm, OperativoForm,
    PartidoPolitico, ResidenciaForm, VotanteForm, CorregimientoForm,
    AsistenciaIndividualForm, AsistenciaColectivaForm)

from datetime import datetime
from dateutil.relativedelta import relativedelta
import openpyxl


"""
    AUTENTICACIÓN
"""
@login_required(redirect_field_name='')    
def registro(request):
    if request.user.is_admin:
        ctx = {
            "form": CustomCreationForm()
        }
        return render(request, "registration/registro.html", ctx)
    else:
        return redirect(to="inicio")
    

"""
    INICIO
"""
@login_required(redirect_field_name='')
def inicio(request):
    votantes = Votante.objects.filter(bloqueado=False)
    centros_votacion = CentroVotacion.objects.all()
    beneficios_faltantes = Beneficio.objects.filter(cantidad=0)

    # GRAFICOS
    # operativos = Operativo.objects.filter(fecha__lt=(datetime.today() - timedelta(days=1)))[:4]
    mitad_votantes = (len(votantes) / 100) * 25
    beneficios = Beneficio.objects.filter(cantidad__lt=mitad_votantes).order_by('cantidad').values()[:4]    
    
    operativos = Operativo.objects.all()[:4]
    asistencias = []
    for op in operativos:
        asistencias.append(op.asistencias.all().count())
    
    corregimientos = Corregimiento.objects.all()
    votantes_corregimiento = []
    for co in corregimientos:
        votantes_corregimiento.append(co.votantes.all().count())
    
    ctx = {
        "votantes": votantes,
        "centros_votacion": centros_votacion,
        "beneficios_faltantes": beneficios_faltantes,
        "beneficios": beneficios,
        "operativos": operativos,
        "asistencias": asistencias,
        "corregimientos": corregimientos,
        "votantes_corregimiento": votantes_corregimiento,
    }

    return render(request, "index.html", ctx)

@login_required(redirect_field_name='')
def validar_votante(request, cedula):
    votante = Votante.objects.filter(bloqueado=False,cedula=cedula).first()
    if votante:
        message = f"El votante se encuentra registrado"
        status = "success"
        content = render_to_string('modals/votanteRegistrado.html', { "votante":votante })

        return JsonResponse({ "message":message, "status":status, "content":content }, safe=False)

    else:
        message = f"No se encuentra registrado el votante ({cedula})"
        status = "warning"

        return JsonResponse({ "message":message, "status":status }, safe=False)

@login_required(redirect_field_name='')
def limitar_votantes(request):
    if request.method == "POST":
        excel_file = request.FILES["votantes_file"]
        # VALIDAR EXCEL
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb.active
        cedulas = list()
        for row in worksheet.iter_rows():
            if row[0].value:
                cedulas.append(row[0].value)

        if cedulas:
            Votante.objects.all().update(bloqueado=True)
            for cedula in cedulas:
                Votante.objects.filter(cedula=cedula).update(bloqueado=False)
            messages.success(request, f"Limitado a {len(cedulas)} votantes")
        else:
            messages.info(request, "No se puedo limitar los votantes",extra_tags="danger")

    return redirect(to="inicio")

@login_required(redirect_field_name='')
def desbloquear_votantes(request):
    Votante.objects.all().update(bloqueado=False)
    return redirect(to="inicio")

@login_required(redirect_field_name='')
def opciones(request):
    
    if request.method == "POST":
        value = request.POST['tema'] 
        Usuario.objects.filter(id=request.user.id).update(tema=value)
        return redirect(to="opciones")
    
    return render(request, "opciones.html")


"""
    OPERATIVO
"""
@login_required(redirect_field_name='')
def listar_operativos(request):
    # operativos = Operativo.objects.filter(fecha__lte=datetime.today()).order_by('fecha')[:10]
    operativos = Operativo.objects.all()
    votantes = Votante.objects.filter(bloqueado=False)
    
    data = []
    for op in operativos:
        be_list = []
        for be in op.beneficios.all():
            be_list.append([be.pk, be.nombre, be.cantidad])
        data.append({
            "id": op.pk,
            "fecha": op.fecha.strftime("%d-%m-%Y %H:%M"),
            "titulo": op.titulo.capitalize(),
            "beneficios": be_list,
        })
        
    ctx = {
        "operativos": operativos,
        "votantes": votantes,
        "data": data,
    }
    
    if request.method == "POST":
        cedula = request.POST["votante"]
        if (Votante.objects.filter(bloqueado=False,cedula=cedula).count() < 1):
            messages.warning(request,"El votante no esta registrado")
            return redirect(to="operativos")
        
        votante = get_object_or_404(Votante, cedula=cedula)
        operativo = get_object_or_404(Operativo, id=request.POST["operativo"])
        
        beneficios = request.POST["beneficios"] #1 PASAR CANTIDAD
        en_c = []
        en_i = []   
        if beneficios:
            beneficios = beneficios.split(',')
            for id in beneficios:
                beneficio = get_object_or_404(Beneficio, id=id)
                entrega = Entrega.objects.create(
                    beneficio=beneficio,
                    cantidad=1,
                )
                if beneficio.tipo == "C":
                    en_c.append(entrega)
                elif beneficio.tipo == "I":
                    en_i.append(entrega)

        if en_c != []:
            if (Residencia.objects.filter(votantes=votante).count() < 1):
                messages.warning(request,"El votante no esta registrado en una residencia",extra_tags="danger")
            
            else:
                residencia = Residencia.objects.filter(votantes=votante).first()
                
                if (AsistenciaColectiva.objects.filter(residencia=residencia, operativo=operativo)):
                    messages.info(request,"La residencia del votante recibió el beneficio")
                
                else:                
                    asistencia_c = AsistenciaColectiva.objects.create(
                        residencia = residencia,
                        operativo = operativo,
                    )
                    for e in en_c:
                        asistencia_c.entregas.add(e)
                        be = e.beneficio
                        be.cantidad -= int(e.cantidad)
                        be.save()
                    messages.success(request, "Ayuda residencial registrada correctamente")

        if (AsistenciaIndividual.objects.filter(votante=votante, operativo=operativo)):
            messages.info(request,"El votante ya registró asistencia")
            return redirect(to="operativos")
        
        asistencia_i = AsistenciaIndividual.objects.create(
            votante=votante,
            operativo=operativo
        )
        if en_i != []:
            for e in en_i:
                asistencia_i.entregas.add(e)
                be = e.beneficio
                be.cantidad -= int(e.cantidad)
                be.save()

        messages.success(request, f"Asistencia del votante registrada correctamente")
            
        return redirect(to="operativos")
   
    return render(request, "operativo/listar.html", ctx)

@login_required(redirect_field_name='')
def agendar_operativo(request):
    ctx = {
        "form": OperativoForm(),
    }
    
    if request.method == "POST":
        data = OperativoForm(data=request.POST)
        if data.is_valid():
            data.save()
            date = data.cleaned_data["fecha"].strftime("%d-%m-%Y %H:%M")
            messages.success(request, f'Operativo agendado {date}')
                            
        else:
            ctx["form"] = data
        
    return render(request, "operativo/agendar.html", ctx)

@login_required(redirect_field_name='')
def administrar_operativo(request, id):
    operativo = get_object_or_404(Operativo, id=id)
    asistencias_i = AsistenciaIndividual.objects.filter(operativo=operativo)
    asistencias_c = AsistenciaColectiva.objects.filter(operativo=operativo)
    # votantes = Votante.objects.filter(operativos=id)
    
    if request.user.is_admin:
        ctx = {
            "form": OperativoForm(instance=operativo),
            "operativo": operativo,
            "asistencias_i": asistencias_i,
            "asistencias_c": asistencias_c
        }
        
        if request.method == "POST":
            data = OperativoForm(data=request.POST, instance=operativo)
            if data.is_valid():
                data.save()
                    
                messages.info(request, "Operativo editado correctamente")
                return redirect(to="operativos")
            else:
                ctx["form"] = data
        
        return render(request, "operativo/administrar.html", ctx)
    
    else:
        messages.warning(request, "No tienes permisos de administrar operativos", extra_tags="danger")
        return redirect(to="operativos")

@login_required(redirect_field_name='')
def eliminar_operativo(request, id):
    operativo = get_object_or_404(Operativo, id=id)
    if request.user.is_admin:
        operativo.delete()
        messages.info(request, "Operativo eliminado")
    else:
        messages.warning(request, "No puede eliminar operativos", extra_tags="danger")
        
    return redirect(to="operativos")

@login_required(redirect_field_name='')
def datatable_asistencias(request, id):
    operativo = get_object_or_404(Operativo, id=id)
    data = []
    
    asistencias_i = AsistenciaIndividual.objects.filter(operativo=operativo)    
    for ai in asistencias_i:        
        beneficios = []
        for en in ai.entregas.all():
            beneficios.append({"nombre":en.beneficio.nombre, "cantidad": en.cantidad})
        
        data.append({
            "id": ai.pk,
            "tipo": "I",
            "asistencia": ai.votante.nombre,
            "beneficios": beneficios,
            "hora": ai.fecha.strftime('%H:%M'),
        })
        
    asistencias_c = AsistenciaColectiva.objects.filter(operativo=operativo)    
    for ac in asistencias_c:        
        beneficios = []
        for en in ac.entregas.all():
            beneficios.append({"nombre":en.beneficio.nombre, "cantidad": en.cantidad})
        
        data.append({
            "id": ac.pk,
            "tipo": "C",
            "asistencia": f"{ac.residencia.numero_casa} ({ac.residencia.barriada})",
            "beneficios": beneficios,
            "hora": ac.fecha.strftime('%H:%M'),
        })
            
    return JsonResponse({'data': data}, safe=False)


"""
    VOTANTE
"""

@login_required(redirect_field_name='')
def listar_votantes(request):
    votantes = Votante.objects.filter(bloqueado=False)
        
    return render(request, "votante/listar.html", {"votantes": votantes})

@login_required(redirect_field_name='')
def datatable_votantes(request):
    votantes = Votante.objects.filter(bloqueado=False)
    data = []
    for vo in votantes:
        # d_related =  vo.dirigente_related.first()

        # if d_related:
        #     dirigente = f"{d_related.dirigente.nombre} ({d_related.dirigente.cedula})"
        # residencia = Residencia.objects.filter(votantes=vo).first()
        corregimiento = Corregimiento.objects.filter(votantes=vo).first()
        es_candidato = ' <i class="fa-solid fa-street-view me-1"></i>' if corregimiento and corregimiento.candidato == vo else ""
        
        if vo.centro_votacion:
            cv = f"{vo.centro_votacion} {f'({vo.mesa})' if vo.mesa else '(N/A)'}"
        else:
            cv = ""

        data.append({
            "id": vo.pk,
            "nombre": vo.nombre.capitalize(),
            "cedula": vo.cedula,
            "corregimiento": f"{es_candidato}{corregimiento.nombre} ({corregimiento.votantes.count()})" if corregimiento else "N/A",
            "dirigente": f"{vo.dirigente.nombre.capitalize()} ({vo.dirigente.cedula})" if vo.dirigente else "N/A",
            "centro_votacion": cv.capitalize() if cv != "" else "N/A",
            "fecha_inscripcion": vo.fecha_inscripcion.strftime("%d-%m-%Y %H:%M"),
        })
    return JsonResponse({'data': data}, safe=False)

@login_required(redirect_field_name='')
def agregar_votante(request):
    ctx = {
        "form": VotanteForm(),
    }
    
    if request.method == "POST":
        data = VotanteForm(data=request.POST)
        if data.is_valid() and not Votante.objects.filter(bloqueado=False,cedula=data.cleaned_data['cedula']).exists():
            obj = data.save(commit=False)            
            edad = relativedelta(datetime.now(), obj.fecha_nacimiento)
            obj.edad = edad.years            
            obj.save()
            messages.success(request, f"Votante {obj.nombre.capitalize()} agregado")
        else:
            messages.warning(request, f"El votante ya esta registrado")
            ctx["form"] = data
        
    return render(request, "votante/agregar.html", ctx)

@login_required(redirect_field_name='')
def editar_votante(request, id):
    votante = get_object_or_404(Votante, id=id)
    
    if request.user.is_admin:
        ctx = {
            "form": VotanteForm(instance=votante),
            "votante": votante
        }
        
        if request.method == "POST":
            data = VotanteForm(data=request.POST, instance=votante)
            if data.is_valid():
                data.save()
                messages.info(request, "Votante editado correctamente")
                return redirect(to="votantes")
            else:
                ctx["form"] = data
        
        return render(request, "votante/editar.html", ctx)
    
    else:
        messages.warning(request, "No tienes permisos de editar votantes", extra_tags="danger")
        return redirect(to="votantes")

@login_required(redirect_field_name='')
def eliminar_votante(request, id):
    votante = get_object_or_404(Votante, id=id)
    if request.user.is_admin:
        votante.delete()
        messages.info(request, "Votante eliminado")
    else:
        messages.warning(request, "No tienes permisos de eliminar votantes", extra_tags="danger")
        
    return redirect(to="votantes")


"""
    RESIDENCIA
"""
@login_required(redirect_field_name='')
def listar_residencias(request):
    residencias = Residencia.objects.all()
        
    return render(request, "residencia/listar.html", {"residencias": residencias})

@login_required(redirect_field_name='')
def datatable_residencias(request):
    residencias = Residencia.objects.all()    
    data = []
    for re in residencias:
        votantes = []
        for v in re.votantes.all():
            votantes.append({"id": v.pk, "nombre": v.nombre.capitalize(), "cedula": v.cedula})
        
        data.append({
            "id": re.pk,
            "numero_casa": re.numero_casa,
            "barriada": re.barriada,
            "sector": re.sector,
            "votantes": votantes,
        })
            
    return JsonResponse({'data': data})

@login_required(redirect_field_name='')
def agregar_residencia(request):
    ctx = {
        "form": ResidenciaForm(),
    }
    
    if request.method == "POST":
        data = ResidenciaForm(data=request.POST)
        if data.is_valid() and not Residencia.objects.filter(numero_casa=data.cleaned_data['numero_casa']).exists():
            data.save()            
            # obj = data.save(commit=False)            
            # edad = relativedelta(datetime.now(), obj.fecha_nacimiento)
            # obj.edad = edad.years            
            # obj.save()
            messages.success(request, f'Residencia registrada')
        else:
            messages.warning(request, f'La residencia ya esta registrada')
            ctx["form"] = data
        
    return render(request, "residencia/agregar.html", ctx)

@login_required(redirect_field_name='')
def editar_residencia(request, id):
    residencia = get_object_or_404(Residencia, id=id)
    
    if request.user.is_admin:
        ctx = {
            "form": ResidenciaForm(instance=residencia),
            "residencia": residencia
        }
        
        if request.method == "POST":
            data = ResidenciaForm(data=request.POST, instance=residencia)
            if data.is_valid():
                data.save()
                messages.info(request, "Residencia editada correctamente")
                return redirect(to="residencias")
            else:
                ctx["form"] = data
        
        return render(request, "residencia/editar.html", ctx)
    
    else:
        messages.warning(request, "No tienes permisos de editar residencias", extra_tags="danger")
        return redirect(to="residencias")

@login_required(redirect_field_name='')
def eliminar_residencia(request, id):
    residencia = get_object_or_404(Residencia, id=id)
    if request.user.is_admin:
        residencia.delete()
        messages.info(request, "Residencia eliminada")
    else:
        messages.warning(request, "No tienes permisos de eliminar residencias", extra_tags="danger")
        
    return redirect(to="residencias")


"""
    CORREGIMIENTO
"""
@login_required(redirect_field_name='')
def listar_corregimientos(request):
    corregimientos = Corregimiento.objects.all()
        
    return render(request, "corregimiento/listar.html", {"corregimientos": corregimientos})

@login_required(redirect_field_name='')
def datatable_corregimientos(request):
    corregimientos = Corregimiento.objects.all()    
    data = []
    for co in corregimientos:   
        data.append({
            "id": co.pk,
            "nombre": co.nombre,
            "candidato": co.candidato.nombre if co.candidato else 'No asignado',
        })
            
    return JsonResponse({'data': data})

@login_required(redirect_field_name='')
def agregar_corregimiento(request):
    ctx = {
        "form": ResidenciaForm(),
    }
    
    if request.method == "POST":
        data = ResidenciaForm(data=request.POST)
        if data.is_valid() and not Residencia.objects.filter(numero_casa=data.cleaned_data['numero_casa']).exists():
            data.save()            
            # obj = data.save(commit=False)            
            # edad = relativedelta(datetime.now(), obj.fecha_nacimiento)
            # obj.edad = edad.years            
            # obj.save()
            messages.success(request, f'Residencia registrada')
        else:
            messages.warning(request, f'La residencia ya esta registrada')
            ctx["form"] = data
        
    return render(request, "residencia/agregar.html", ctx)

@login_required(redirect_field_name='')
def editar_corregimiento(request, id):
    residencia = get_object_or_404(Residencia, id=id)
    
    if request.user.is_admin:
        ctx = {
            "form": ResidenciaForm(instance=residencia),
            "residencia": residencia
        }
        
        if request.method == "POST":
            data = ResidenciaForm(data=request.POST, instance=residencia)
            if data.is_valid():
                data.save()
                messages.info(request, "Residencia editada correctamente")
                return redirect(to="residencias")
            else:
                ctx["form"] = data
        
        return render(request, "residencia/editar.html", ctx)
    
    else:
        messages.warning(request, "No tienes permisos de editar residencias", extra_tags="danger")
        return redirect(to="residencias")

@login_required(redirect_field_name='')
def eliminar_corregimiento(request, id):
    residencia = get_object_or_404(Residencia, id=id)
    if request.user.is_admin:
        residencia.delete()
        messages.info(request, "Residencia eliminada")
    else:
        messages.warning(request, "No tienes permisos de eliminar residencias", extra_tags="danger")
        
    return redirect(to="residencias")


"""
    DIRIGENTE
"""
@login_required(redirect_field_name='')
def listar_dirigentes(request):
    dirigentes = Dirigente.objects.all()
        
    return render(request, "dirigente/listar.html", {"dirigentes": dirigentes})

@login_required(redirect_field_name='')
def datatable_dirigentes(request):
    dirigentes = Dirigente.objects.all()    
    data = []
    for di in dirigentes:        
        vo = Votante.objects.filter(dirigente=di)
            
        data.append({
            "id": di.pk,
            "nombre": di.nombre+' (apoyo)' if di.es_apoyo else di.nombre,
            "cedula": di.cedula,
            "votantes": vo.count(),
        })
            
    return JsonResponse({'data': data})

@login_required(redirect_field_name='')
def agregar_dirigente(request):
    ctx = {
        "form": DirigenteForm(),
    }
    
    if request.method == "POST":
        data = DirigenteForm(data=request.POST)
        if data.is_valid() and not Dirigente.objects.filter(cedula=data.cleaned_data['cedula']).exists():
            data.save()
            messages.success(request, f'Dirigente agregado')
        else:
            messages.warning(request, f'La cédula {data.cleaned_data["cedula"]} ya esta registrada')
            ctx["form"] = data
        
    return render(request, "dirigente/agregar.html", ctx)

@login_required(redirect_field_name='')
def editar_dirigente(request, id):
    dirigente = get_object_or_404(Dirigente, id=id)
    di_votante = Votante.objects.filter(cedula=dirigente.cedula).first()
    votantes = Votante.objects.exclude(cedula=dirigente.cedula)
    
    if request.user.is_admin:
        ctx = {
            "dirigente": dirigente,
            "votantes": votantes if votantes else None,
        }
        
        if request.method == "POST":
            for vo in votantes.filter(dirigente=dirigente):
                vo.dirigente = None
                vo.save()
            
            if request.POST.get("votantes", False):
                data = json.loads(str(request.POST).replace("<QueryDict: ", "").replace(">", "").replace("'", "\""))
                for vo in data.get("votantes", None):
                    v = get_object_or_404(Votante, id=vo)
                    v.dirigente = dirigente
                    v.save()
                
            di_votante.nombre = request.POST.get("nombre", dirigente.nombre)
            di_votante.cedula = request.POST.get("cedula", dirigente.cedula)
            di_votante.telefono = request.POST.get("telefono", dirigente.telefono)
            di_votante.save()
            dirigente.nombre = request.POST.get("nombre", dirigente.nombre)
            dirigente.cedula = request.POST.get("cedula", dirigente.cedula)
            dirigente.telefono = request.POST.get("telefono", dirigente.telefono)
            dirigente.es_apoyo = True if request.POST.get("es_apoyo") == "1" else False
            dirigente.save()
            
            messages.info(request, "Dirigente editado correctamente")
            return redirect(to="dirigentes")
        
        return render(request, "dirigente/editar.html", ctx)
    
    else:
        messages.warning(request, "No tienes permisos de editar dirigentes", extra_tags="danger")
        return redirect(to="dirigentes")

@login_required(redirect_field_name='')
def eliminar_dirigente(request, id):
    dirigente = get_object_or_404(Dirigente, id=id)
    if request.user.is_admin:
        dirigente.delete()
        messages.info(request, "Dirigente eliminado")
    else:
        messages.warning(request, "No tienes permisos de eliminar dirigentes", extra_tags="danger")
        
    return redirect(to="dirigentes")


"""
    INVENTARIO
"""
@login_required(redirect_field_name='')
def listar_beneficios(request):
    beneficios = Beneficio.objects.all()
        
    return render(request, "beneficio/listar.html", {"beneficios": beneficios})

@login_required(redirect_field_name='')
def datatable_beneficios(request):
    beneficios = list(Beneficio.objects.values('id', 'nombre', 'cantidad', 'tipo'))
    return JsonResponse({'data': beneficios})

@login_required(redirect_field_name='')
def agregar_beneficio(request):
    ctx = {
        "form": BeneficioForm(),
    }
    
    if request.method == "POST":
        data = BeneficioForm(data=request.POST)
        nombre = request.POST["nombre"]
        
        if data.is_valid() and not Beneficio.objects.filter(nombre=nombre).exists():
            data.save()
            messages.success(request, f'Beneficio agregado correctamente')
        else:
            messages.warning(request, f'"{nombre}" ya esta registrado')
            ctx["form"] = data
        
    return render(request, "beneficio/agregar.html", ctx)

@login_required(redirect_field_name='')
def editar_beneficio(request, id):
    beneficio = get_object_or_404(Beneficio, id=id)
    
    if request.user.is_admin:
        ctx = {
            "form": BeneficioForm(instance=beneficio),
            "beneficio": beneficio
        }
        
        if request.method == "POST":
            data = BeneficioForm(data=request.POST, instance=beneficio)
            if data.is_valid():
                data.save()
                messages.info(request, "Beneficio editado correctamente")
                return redirect(to="beneficios")
            else:
                ctx["form"] = data
        
        return render(request, "beneficio/editar.html", ctx)
    
    else:
        messages.warning(request, "No tienes permisos de editar beneficios", extra_tags="danger")
        return redirect(to="beneficios")

@login_required(redirect_field_name='')
def eliminar_beneficio(request, id):
    beneficio = get_object_or_404(Beneficio, id=id)
    if request.user.is_admin:
        beneficio.delete()
        messages.info(request, "Benficio eliminado")
    else:
        messages.warning(request, "No tienes permisos de eliminar beneficios", extra_tags="danger")
        
    return redirect(to="beneficios")


"""
    EVENTOS
"""
@login_required(redirect_field_name='')
def listar_eventos(request, tipo):
    eventos = EventoLog.objects.filter(tipo=tipo) if tipo != None else EventoLog.objects.all()
   
    print(EventoLog.tipo.attname)
    
    ctx = {
        "eventos": eventos,
    }
    
    if request.method == "POST":
        pass
        
    return render(request, "dirigente/eventos.html", ctx)