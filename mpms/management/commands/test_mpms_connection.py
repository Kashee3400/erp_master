from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):
    help = 'Test connection to mpms database'

    def handle(self, *args, **kwargs):
        try:
            connection = connections['mpms_db']
            cursor = connection.cursor()
            cursor.execute('SELECT 1')
            self.stdout.write(self.style.SUCCESS('Successfully connected to mpms database.'))
            cursor.execute("SELECT * FROM dbo.entry_table")
            rows = cursor.fetchall()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
