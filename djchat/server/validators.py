import os

from django.core.exceptions import ValidationError
from PIL import Image


def validate_icon_image_size(image):
    if image:
        with Image.open(image) as img:
            if img.width > 200 or img.height > 200:
                raise ValidationError(f"Image size too big, please upload 70x70")


def validate_image_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = [".jpg", ".svg", ".png", ".jpeg", ".gif"]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported file extension")
