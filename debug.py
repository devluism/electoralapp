import subprocess

class Script():
    def __init__(self):
        subprocess.getoutput("rm ./*db*")
        subprocess.getoutput("rm ./electoral/migrations/*00*")
        subprocess.getoutput("touch ./db.sqlite3")
        subprocess.getoutput("python manage.py makemigrations")
        subprocess.getoutput("python manage.py migrate")
        subprocess.getoutput("echo from electoral.models import Usuario; Usuario.objects.create_superuser('admin', 'admin', 'admin') | python manage.py shell")

if __name__ == '__main__':
    execute = Script()
