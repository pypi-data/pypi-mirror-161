import os.path
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image


def get_image(name="test.png", width=160, height=100):
    image = Image.new("RGB", (width, height), color="red")

    with BytesIO() as output:
        image.save(output, os.path.splitext(name)[1][1:])
        return ContentFile(output.getvalue(), name=name)
