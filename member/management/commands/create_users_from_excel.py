import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

class Command(BaseCommand):
    help = 'Create users from an Excel file'

    def handle(self, *args, **kwargs):
        # Path to the Excel file
        excel_file_path = 'path/to/your/excel_file.xlsx'

        # Read the Excel file
        df = pd.read_excel(excel_file_path)

        # Define the default password
        default_password = '12345@Kashee'

        for index, row in df.iterrows():
            # Assuming the Excel file has columns named 'username', 'first_name', 'last_name', 'email'
            username = row['username']
            first_name = row.get('first_name', '')
            last_name = row.get('last_name', '')
            email = row.get('email', '')

            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'User {username} already exists. Skipping.'))
                continue

            # Create the user
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=default_password
            )

            self.stdout.write(self.style.SUCCESS(f'User {username} created successfully.'))

        self.stdout.write(self.style.SUCCESS('All users have been processed.'))
