# utils/fields.py
import base64
import imghdr
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    A Django REST Framework field for handling image-uploads through raw post data.
    It uses base64 for encoding/decoding the contents of the file.
    """

    def to_internal_value(self, data):
        # If already a file, just process normally
        if isinstance(data, ContentFile):
            return super().to_internal_value(data)

        # If it's a base64 string
        if isinstance(data, str):
            try:
                # Remove header like "data:image/jpeg;base64,"
                if ";base64," in data:
                    data = data.split(";base64,")[1]

                decoded_file = base64.b64decode(data)
                file_name = str(uuid.uuid4())[:12]  # 12 char uuid
                file_extension = imghdr.what(None, decoded_file)
                if file_extension is None:
                    file_extension = "jpg"
                complete_file_name = f"{file_name}.{file_extension}"
                data = ContentFile(decoded_file, name=complete_file_name)
            except Exception:
                raise serializers.ValidationError("Invalid base64 image data")

        return super().to_internal_value(data)
