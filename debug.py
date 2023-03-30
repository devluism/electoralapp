import subprocess

class Script():
    def __init__(self):
        subprocess.getoutput("rm ./*database*")
        subprocess.getoutput("rm ./electoral/migrations/*00*")
        subprocess.getoutput("touch ./database.db")
        #subprocess.getoutput("python manage.py makemigrations")
        #subprocess.getoutput("python manage.py migrate")
        #subprocess.getoutput("echo from electoral.models import Usuario; Usuario.objects.create_superuser('admin', 'admin', 'admin') | python manage.py shell")

if __name__ == '__main__':
    execute = Script()
