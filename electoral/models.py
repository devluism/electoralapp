from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractUser)

class CentroVotacion(models.Model):
    cede=models.CharField(max_length=250,unique=True)
    barrio=models.CharField(max_length=250,null=True,blank=True)
    sector=models.CharField(max_length=250,null=True,blank=True)
    direccion=models.TextField(max_length=500,null=True,blank=True)
    
    class Meta:
        ordering = ["id"]
        verbose_name = "centro de votación"
        verbose_name_plural = "centros de votación"
        
    def __str__(self):
        return self.cede
    
class Mesa(models.Model):
    codigo=models.CharField(max_length=250,unique=True)
    centro_votacion=models.ForeignKey(CentroVotacion,models.SET_NULL,verbose_name="Centro de votación",null=True,blank=True)
    
    class Meta:
        ordering = ["id"]
        verbose_name = "mesa"
        verbose_name_plural = "mesas"
        
    def __str__(self):
        texto = "{0} - ({1})"
        return texto.format(self.codigo, self.centro_votacion)

class UsuarioManager(BaseUserManager):
    def create_user(self, cedula, telefono, password=None):
        """
        Creates and saves a User with the given cedula, telefono and password.
        """
        if not cedula:
            raise ValueError('Los usuarios deben tener una cédula')

        user = self.model(
            cedula=cedula,
            telefono=telefono,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, cedula, telefono, password=None):
        """
        Creates and saves a superuser with the given cedula, telefono and password.
        """
        user = self.create_user(
            cedula,
            password=password,
            telefono=telefono,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class Usuario(AbstractUser):
    THEME = [
        ("light", "light"),
        ("dark", "dark"),
    ]

    nombre=models.CharField(max_length=50,null=True,blank=True)
    cedula=models.CharField(verbose_name="Cédula",max_length=25,unique=True)
    telefono=models.CharField(verbose_name="Teléfono",max_length=25,null=True,blank=True)
    tema=models.CharField(max_length=10,choices=THEME,default="light")

    last_login=None
    email=None
    username=None
    first_name=None
    last_name=None
    is_active=models.BooleanField(verbose_name="Activo",default=True)
    is_admin=models.BooleanField(verbose_name="Es administrador",default=False)

    objects=UsuarioManager()

    EMAIL_FIELD="telefono"
    USERNAME_FIELD="cedula"
    REQUIRED_FIELDS=["telefono"]

    class Meta:
        ordering = ["id"]
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
    
    def __str__(self):
        texto = "{0} ({1})"
        return texto.format(self.nombre, self.cedula)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class Beneficio(models.Model):
    TIPO = [
        ("I", "Individual"),
        ("C", "Colectivo"),
    ]
    nombre=models.CharField(max_length=50, unique=True)
    cantidad=models.PositiveIntegerField(default=1)
    tipo=models.CharField(max_length=50,choices=TIPO,default="I")
    
    class Meta:
        ordering = ["id"]
        verbose_name = "beneficio"
        verbose_name_plural = "beneficios"
    
    def __str__(self):
        texto = "{0} ({1})"
        return texto.format(self.nombre,self.cantidad)
    
class Operativo(models.Model):
    titulo=models.CharField(max_length=50,verbose_name="Título")
    cede=models.CharField(max_length=50,null=True,blank=True)
    barrio=models.CharField(max_length=50,null=True,blank=True)
    sector=models.CharField(max_length=50,null=True,blank=True)
    direccion=models.TextField(verbose_name="Dirección",max_length=500,null=True,blank=True)
    fecha=models.DateTimeField(null=True,blank=True)
    beneficios=models.ManyToManyField(Beneficio,default="Ninguno",related_name='operativos',blank=True)
    
    class Meta:
        ordering = ["id"]
        verbose_name = "operativo"
        verbose_name_plural = "operativos"
    
    def __str__(self):
        texto = "{0} ({1})"
        return texto.format(self.titulo,self.fecha)

class PartidoPolitico(models.Model):
    nombre=models.CharField(max_length=50,null=True,blank=True)   
    creado_en=models.DateField(auto_now=True)
    
    class Meta:
        ordering = ["id"]
        verbose_name = "Partido político"
        verbose_name_plural = "Partidos políticos"

    def __str__(self):
        return self.nombre

class Dirigente(models.Model):
    nombre=models.CharField(max_length=150)
    cedula=models.CharField(verbose_name="Cédula",max_length=50,unique=True)
    es_apoyo=models.BooleanField(verbose_name="Apoyo",default=False)
    
    #1 Faltan campos del xlsx
    telefono=models.CharField(verbose_name="Teléfono",max_length=50,null=True,blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "dirigente"
        verbose_name_plural = "dirigentes"
    
    def __str__(self):
        return f"{self.nombre} {self.cedula} {'(Apoyo)' if self.es_apoyo else '' }"

class Votante(models.Model):
    SEXO = [
        ("M", "Masculino"),
        ("F", "Femenino"),
    ]
    
    bloqueado=models.BooleanField(default=False)
    # foto=models.FileField(upload_on="images/votantes/")
    # codigo=models.CharField(verbose_name="Código",max_length=50,null=True,blank=True)
    nombre=models.CharField(max_length=150)
    cedula=models.CharField(verbose_name="Cédula",max_length=50,unique=True)
    fecha_nacimiento=models.DateField(null=True,blank=True)
    edad=models.PositiveIntegerField(null=True,blank=True)
    telefono=models.CharField(verbose_name="Teléfono",max_length=50,null=True,blank=True)
    sexo=models.CharField(max_length=50,choices=SEXO,default="M")
    fecha_inscripcion=models.DateTimeField(auto_now=True)

    dirigente=models.ForeignKey(Dirigente,models.SET_NULL,related_name='votantes',null=True,blank=True)
    centro_votacion=models.ForeignKey(CentroVotacion,models.SET_NULL,verbose_name="Centro de votación",related_name='votantes',null=True,blank=True)
    mesa=models.PositiveIntegerField(null=True,blank=True)
    partido_politico=models.ForeignKey(PartidoPolitico,models.SET_NULL,verbose_name="Partido político",related_name='votantes',null=True,blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "votante"
        verbose_name_plural = "votantes"
    
    def __str__(self):
        return f"{self.nombre} ({self.cedula})"

class Residencia(models.Model):
    numero_casa=models.CharField(verbose_name="N° Casa",max_length=50,null=True,blank=True)
    barriada=models.CharField(max_length=250,null=True,blank=True)
    sector=models.CharField(max_length=50,null=True,blank=True)
    direccion=models.TextField(verbose_name="Dirección",max_length=500,null=True,blank=True)
    votantes=models.ManyToManyField(Votante,related_name='residencia',default="Ninguno",blank=True)
    
    class Meta:
        ordering = ["id"]
        verbose_name = ("residencia")
        verbose_name_plural = ("residencias")

    def __str__(self):
        return f"{self.numero_casa} - {self.barriada}"

class Corregimiento(models.Model):
    nombre=models.CharField(max_length=150,unique=True,null=False,blank=False)
    candidato=models.ForeignKey(Votante,models.SET_NULL,related_name='corregimiento_related',null=True)
    residencias=models.ManyToManyField(Residencia,related_name='corregimiento',default="Ninguno",blank=True)
    votantes=models.ManyToManyField(Votante,related_name='corregimiento',default="Ninguno",blank=True)
    
    class Meta:
        ordering = ["id"]
        verbose_name = "corregimiento"
        verbose_name_plural = "corregimientos"
    
    def __str__(self):
        return self.nombre

class Entrega(models.Model):
    beneficio=models.ForeignKey(Beneficio,models.SET_NULL,null=True,blank=True)
    cantidad=models.PositiveIntegerField()
    fecha=models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["id"]
        verbose_name = "entrega"
        verbose_name_plural = "entregas"
        
    def __str__(self):
        texto = "{0} ({1})"
        return texto.format(self.beneficio, self.cantidad)
    
class AsistenciaIndividual(models.Model):
    votante=models.ForeignKey(Votante,models.CASCADE)
    operativo=models.ForeignKey(Operativo,models.CASCADE,related_name='asistencias')
    entregas=models.ManyToManyField(Entrega,related_name='asistencias',default="Ninguno",blank=True)
    fecha=models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["id"]
        verbose_name = "asistencia individual"
        verbose_name_plural = "asistencias individuales"
        
    def __str__(self):
        texto = "{0} ({1}) - {2}"
        return texto.format(self.votante, self.fecha, self.operativo)
    
class AsistenciaColectiva(models.Model):
    residencia=models.ForeignKey(Residencia,models.CASCADE)
    operativo=models.ForeignKey(Operativo,models.CASCADE)
    entregas=models.ManyToManyField(Entrega,related_name='asistencias_colectivas')
    fecha=models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["id"]
        verbose_name = "asistencia colectiva"
        verbose_name_plural = "asistencias colectivas"
        
    def __str__(self):
        texto = "{0} ({1}) - {2}"
        return texto.format(self.residencia, self.fecha, self.operativo)


    
