from django.conf import settings
from geoip2.database import Reader
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os


def get_geo_location(ip):
    try:
        reader = Reader(settings.GEOIP_PATH + '/GeoLite2-City.mmdb')
        response = reader.city(ip)
        return f"{response.city.name}, {response.country.name}"
    except:
        return "Unknown"


def generate_image_thumbnail(instance):
    try:
        image = Image.open(instance.file)
        image.thumbnail((300, 300))
        thumb_io = BytesIO()
        image.save(thumb_io, format='JPEG')
        instance.thumbnail.save(f"thumb_{instance.file.name}", ContentFile(thumb_io.getvalue()), save=True)
    except Exception as e:
        print("Thumbnail error:", e)

def get_client_ip(request):
    return request.META.get('REMOTE_ADDR', '127.0.0.1')

def get_geo_location(ip):
    try:
        reader = Reader(os.path.join(settings.GEOIP_PATH, 'GeoLite2-City.mmdb'))
        r = reader.city(ip)
        return f"{r.city.name}, {r.country.name}"
    except:
        return "Unknown"
