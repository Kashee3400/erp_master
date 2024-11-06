import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from member.models import SahayakIncentives
from urllib.request import urlopen
User = get_user_model()

class Command(BaseCommand):
    help = 'Populate SahayakIncentives table from Excel file on OneDrive'
    
    def handle(self, *args, **kwargs):
        excel_url = 'https://onedrive.live.com/download?cid=Your_CID&resid=Your_RESID&authkey=Your_AUTHKEY'
        with urlopen(excel_url) as response:
            df = pd.read_excel(response)
        for index, row in df.iterrows():
            # Fetch user
            user = User.objects.get(username=row['user'])
            obj, created = SahayakIncentives.objects.update_or_create(
                user=user,
                month=row['month'],
                defaults={
                    'mcc_code': row.get('mcc_code', ''),
                    'mcc_name': row.get('mcc_name', ''),
                    'mpp_code': row.get('mpp_code', ''),
                    'mpp_name': row.get('mpp_name', ''),
                    'opening': row.get('opening', 0.0),
                    'milk_incentive': row.get('milk_incentive', 0.0),
                    'other_incentive': row.get('other_incentive', 0.0),
                    'closing': row.get('closing', 0.0),
                    'payable': row.get('payable', 0.0)
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created incentive for {user.username} for {row["month"]}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated incentive for {user.username} for {row["month"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully populated SahayakIncentives table.'))
