import operator
from typing import Optional

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class FileSizeValidator:
    message = _("Maximum file size is %(size).2g MB.")
    code = "invalid_file_size"

    def __init__(
        self,
        max_file_size: Optional[int] = None,
        message: Optional[str] = None,
        code: Optional[str] = None,
    ):
        self.max_file_size = max_file_size
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        if self.max_file_size is not None and value.size > self.max_file_size:
            raise ValidationError(
                self.message,
                code=self.code,
                params={"size": self.max_file_size / 1024 / 1024},
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.max_file_size == other.max_file_size
            and self.message == other.message
            and self.code == other.code
        )


@deconstructible
class ImageDimensionsValidator:
    code = "invalid_image_dimensions"
    default_messages = {
        "lt": _("Image dimensions must be less than %(dimension)s."),
        "le": _("Image dimensions must be less than or equal to %(dimension)s."),
        "gt": _("Image dimensions must be greater than %(dimension)s."),
        "ge": _("Image dimensions must be greater than or equal to %(dimension)s."),
        "eq": _("Image dimensions must be equal to %(dimension)s."),
        "ne": _("Image dimensions may not be equal to %(dimension)s."),
    }

    def __init__(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        op: Optional[str] = "ge",
        message: Optional[str] = None,
        code: Optional[str] = None,
    ):
        self.width = width
        self.height = height
        self.operator = getattr(operator, op, operator.ge)
        self.message = message or self.default_messages[self.operator.__name__]
        if code is not None:
            self.code = code

    def __call__(self, value):
        if value.closed:
            value.open()
        width, height = get_image_dimensions(value)
        if (
            self.width
            and not self.operator(width, self.width)
            or self.height
            and not self.operator(height, self.height)
        ):
            raise ValidationError(
                self.message,
                code=self.code,
                params={"dimension": self._get_dimensions_format()},
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.width == other.width
            and self.height == other.height
            and self.operator == other.operator
            and self.message == other.message
            and self.code == other.code
        )

    def _get_dimensions_format(self):
        if self.width and self.height:
            return _("%(width)dx%(height)d pixels") % {
                "width": self.width,
                "height": self.height,
            }
        elif self.width:
            return _("%(width)d pixels wide") % {"width": self.width}
        elif self.height:  # pragma: no cover
            return _("%(height)d pixels high") % {"height": self.height}
