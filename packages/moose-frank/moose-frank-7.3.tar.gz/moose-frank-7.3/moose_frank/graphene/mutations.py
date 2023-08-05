from collections import OrderedDict

import graphene
from django.core.files.uploadedfile import UploadedFile
from django.forms import all_valid
from graphene import Field, InputField
from graphene.types.utils import yank_fields_from_attrs
from graphene_django.forms.mutation import DjangoModelDjangoFormMutationOptions
from graphene_django.forms.mutation import (
    DjangoModelFormMutation as BaseDjangoModelFormMutation,
)
from graphene_django.forms.mutation import fields_for_form
from graphene_django.forms.types import ErrorType
from graphene_django.registry import get_global_registry

from .types import ErrorTypeFormset, ErrorUnion


class DjangoModelFormMutation(BaseDjangoModelFormMutation):
    class Meta:
        abstract = True

    @classmethod
    def get_object(cls, root, info, pk):
        return cls._meta.model._default_manager.get(pk=pk)

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        kwargs = {"data": input}
        pk = input.pop("id", None)
        if pk:
            kwargs["instance"] = cls.get_object(root, info, pk)
        return kwargs


class DjangoModelFormWithInlinesMutation(DjangoModelFormMutation):
    errors = graphene.List(ErrorUnion)

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls,
        inlines=None,
        form_class=None,
        model=None,
        return_field_name=None,
        only_fields=(),
        exclude_fields=(),
        **options,
    ):
        if not inlines:
            raise Exception(
                "inlines are required for DjangoModelFormWithInlinesMutation"
            )

        if not form_class:
            raise Exception("form_class is required for DjangoModelFormMutation")

        if not model:
            model = form_class._meta.model

        if not model:
            raise Exception("model is required for DjangoModelFormMutation")

        form = form_class()
        input_fields = fields_for_form(form, only_fields, exclude_fields)
        input_fields["id"] = graphene.ID()

        for field, inline in dict(inlines).items():
            input_fields[f"{field}_total_forms"] = graphene.Int(required=True)
            input_fields[f"{field}_initial_forms"] = graphene.Int(required=True)

            inline_fields = fields_for_form(
                inline.form_class(), inline.fields or (), inline.exclude or ()
            )
            inline_fields["id"] = graphene.ID()
            inline_fields["delete"] = graphene.Boolean(default_value=False)

            inline_input = type(
                "{}Input".format(inline.__name__),
                (graphene.InputObjectType,),
                OrderedDict(yank_fields_from_attrs(inline_fields, _as=InputField)),
            )

            input_fields[field] = graphene.List(inline_input)

        registry = get_global_registry()
        model_type = registry.get_type_for_model(model)
        return_field_name = return_field_name
        if not return_field_name:
            model_name = model.__name__
            return_field_name = model_name[:1].lower() + model_name[1:]

        output_fields = OrderedDict()
        output_fields[return_field_name] = graphene.Field(model_type)

        _meta = DjangoModelDjangoFormMutationOptions(cls)
        _meta.inlines = inlines
        _meta.form_class = form_class
        _meta.model = model
        _meta.return_field_name = return_field_name
        _meta.fields = yank_fields_from_attrs(output_fields, _as=Field)

        input_fields = yank_fields_from_attrs(input_fields, _as=InputField)
        super(BaseDjangoModelFormMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, input_fields=input_fields, **options
        )

    @classmethod
    def get_inlines(cls):
        return cls._meta.inlines

    @classmethod
    def construct_inlines(cls, request, obj, input):
        request.POST = request.POST.copy()

        inline_formsets = []
        for field, inline_class in dict(cls.get_inlines()).items():
            request.POST[f"{field}-TOTAL_FORMS"] = input[f"{field}_total_forms"]
            request.POST[f"{field}-INITIAL_FORMS"] = input[f"{field}_initial_forms"]

            for i, inline_data in enumerate(input.get(field, [])):
                for key, value in inline_data.items():
                    if key == "delete":
                        key = key.upper()

                    if isinstance(value, dict):
                        file = value.get("file", None)
                        if isinstance(file, UploadedFile):
                            request.FILES[f"{field}-{i}-{key}"] = file
                        if value.get("clear", False):
                            request.POST[f"{field}-{i}-{key}-clear"] = True
                    else:
                        request.POST[f"{field}-{i}-{key}"] = value

            inline_instance = inline_class(cls._meta.model, request, obj)
            inline_formset = inline_instance.construct_formset()
            inline_formsets.append(inline_formset)
        return inline_formsets

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        form = cls.get_form(root, info, **input)

        obj = form.instance
        if form.is_valid():
            obj = form.save(commit=False)
            form_validated = True
        else:
            form_validated = False

        inlines = cls.construct_inlines(info.context, obj, input)

        if all_valid(inlines) and form_validated:
            return cls.perform_mutate(form, inlines, info)
        else:
            errors = [
                ErrorType(field=key, messages=value)
                for key, value in form.errors.items()
            ]

            for inline in inlines:
                non_form_errors = inline.non_form_errors()
                if non_form_errors:
                    errors += [ErrorType(field=inline.prefix, messages=non_form_errors)]

                errors += [
                    ErrorTypeFormset(
                        field=inline.prefix,
                        form_index=i,
                        errors=[
                            ErrorType(field=key, messages=value)
                            for key, value in form.errors.items()
                        ],
                    )
                    for i, form in enumerate(inline.forms)
                    if not (inline.can_delete and inline._should_delete_form(form))
                    and form.errors
                ]

            return cls(errors=errors)

    @classmethod
    def perform_mutate(cls, form, inlines, info):
        obj = form.save()
        for formset in inlines:
            formset.save()
        kwargs = {cls._meta.return_field_name: obj}
        return cls(errors=[], **kwargs)
