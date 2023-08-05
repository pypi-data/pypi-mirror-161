from os.path import basename

import graphene
from graphene_django.types import ErrorType
from graphene_file_upload.scalars import Upload

from moose_frank.graphene import settings
from moose_frank.graphene.utils import _get_module_method


_get_thumbnail = _get_module_method(settings.GRAPHENE_THUMBNAIL_METHOD)
_get_async_thumbnail = _get_module_method(settings.GRAPHENE_ASYNC_THUMBNAIL_METHOD)


class ErrorTypeFormset(ErrorType):
    field = graphene.String(required=True)
    form_index = graphene.Int()
    errors = graphene.List(ErrorType)


class ErrorUnion(graphene.Union):
    class Meta:
        types = (ErrorType, ErrorTypeFormset)


class ThumbnailOptionsType(graphene.InputObjectType):
    geometry = graphene.String(required=True)
    asynchronous = graphene.Boolean()
    blur = graphene.Int()
    colorspace = graphene.String()
    crop = graphene.String()
    cropbox = graphene.String()
    format = graphene.String()
    orientation = graphene.Boolean()
    padding = graphene.Boolean()
    padding_color = graphene.String()
    progressive = graphene.Boolean()
    quality = graphene.Int()
    rounded = graphene.Int()
    upscale = graphene.Boolean()


class FileObjectType(graphene.ObjectType):
    filename = graphene.String()
    url = graphene.String()

    def resolve_filename(self, info):
        if not self.name:
            return ""
        return basename(self.name)

    def resolve_url(self, info):
        if not self.name:
            return ""
        return info.context.build_absolute_uri(self.url)


class ImageObjectType(FileObjectType):
    url = graphene.String(options=ThumbnailOptionsType())

    def resolve_url(self, info, options=None):
        if not self.name:
            return ""

        if options:
            options = options.copy()
            geometry = options.pop("geometry")
            async_thumbnail = options.pop("asynchronous", False)

            if async_thumbnail:
                get_thumbnail = _get_async_thumbnail
            else:
                get_thumbnail = _get_thumbnail
            url = get_thumbnail(self, geometry, **options).url
        else:
            url = self.url
        return info.context.build_absolute_uri(str(url))


class UploadInput(graphene.InputObjectType):
    file = Upload()
    clear = graphene.Boolean()
