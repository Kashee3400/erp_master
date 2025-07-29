from django.conf import settings
from geoip2.database import Reader
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
import uuid

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




def upload_passbook_path(instance, filename):
    """Generate upload path for passbook documents"""
    ext = filename.split(".")[-1]
    filename = f"{instance.member_code}_{uuid.uuid4().hex}.{ext}"
    return os.path.join(
        "passbooks/",
        str(instance.requested_at.year),
        str(instance.requested_at.month),
        filename,
    )


def upload_application_path(instance, filename):
    """Generate upload path for application documents"""
    ext = filename.split(".")[-1]
    filename = f"{instance.member_code}_app_{uuid.uuid4().hex}.{ext}"
    return os.path.join(
        "applications/",
        str(instance.requested_at.year),
        str(instance.requested_at.month),
        filename,
    )


def upload_affidavit_path(instance, filename):
    """Generate upload path for affidavit documents"""
    ext = filename.split(".")[-1]
    filename = f"{instance.member_code}_affidavit_{uuid.uuid4().hex}.{ext}"
    return os.path.join(
        "affidavits/",
        str(instance.requested_at.year),
        str(instance.requested_at.month),
        filename,
    )
