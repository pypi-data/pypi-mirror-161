import graphene
from django.contrib.admin.utils import NestedObjects
from django.core.files.uploadedfile import UploadedFile


class CanDeleteMixin:
    can_delete = graphene.Boolean()

    def resolve_can_delete(self, info):
        collector = NestedObjects(using="default")
        collector.collect([self])
        return not collector.protected


class UploadedFilesMixin:
    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        kwargs = super().get_form_kwargs(root, info, **input)
        kwargs["files"] = {}
        for k, v in input.items():
            if isinstance(v, dict):
                file = v.get("file", None)
                if isinstance(file, UploadedFile):
                    kwargs["files"][k] = file
                if v.get("clear", False):
                    kwargs["data"][f"{k}-clear"] = True
        return kwargs


class SingletonFormMixin:
    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        input.pop("id", None)
        return {"data": input, "instance": cls._meta.model.singleton()}
