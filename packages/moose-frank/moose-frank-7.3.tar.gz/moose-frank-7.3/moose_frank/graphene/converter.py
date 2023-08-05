from django import forms
from django.db import models
from graphene import Field
from graphene_django.converter import convert_django_field
from graphene_django.forms.converter import convert_form_field

from moose_frank.graphene.types import FileObjectType, ImageObjectType, UploadInput


def register_file_field():
    @convert_form_field.register(forms.FileField)
    def convert_form_field_to_upload(field):
        return UploadInput(description=field.help_text)

    @convert_django_field.register(models.FileField)
    def convert_field_to_file_field(field, registry=None):
        return Field(
            FileObjectType, description=field.help_text, required=not field.null
        )

    @convert_django_field.register(models.ImageField)
    def convert_field_to_image_field(field, registry=None):
        return Field(
            ImageObjectType, description=field.help_text, required=not field.null
        )
