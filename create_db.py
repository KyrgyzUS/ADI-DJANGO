import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store_project.settings')
django.setup()

from django.core.management import call_command

def create_db():
    call_command('migrate')
    call_command('createsuperuser')

if __name__ == '__main__':
    create_db()
