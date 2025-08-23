from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection, transaction
from django.conf import settings

class Command(BaseCommand):
    help = "Truncate all tables for a specific app"

    def add_arguments(self, parser):
        parser.add_argument("app_label", type=str, help="App label to truncate")

    def handle(self, *args, **options):
        app_label = options["app_label"]
        app_config = apps.get_app_config(app_label)
        confirm = input(
            f"⚠️  You are about to TRUNCATE ALL TABLES in the '{app_label}' app.\n"
            f"This will DELETE ALL DATA and RESET AUTO-INCREMENTS.\n\n"
            f"Type 'yes' to confirm: "
        )
        if confirm.lower() != "yes":
            self.stdout.write("Aborted.")
            return

        with connection.cursor() as cursor:
            for model in app_config.get_models():
                table = model._meta.db_table
                try:
                    self.stdout.write(f"Truncating table: {table}")
                    with transaction.atomic():
                        cursor.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
                except Exception as e:
                    self.stdout.write(f"⚠️  Skipping '{table}': {e}")
