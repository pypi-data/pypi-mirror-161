from urllib.parse import urlparse

from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat, stringfilter
from django.utils.formats import get_format
from django.utils.translation import gettext_lazy as _

from moose_frank.utils import strip_unicode
from moose_frank.utils.filters import decimal_filter


register = template.Library()


@register.simple_tag(takes_context=True)
def paginator_get_params(context, page_number):
    params = context["request"].GET.copy()
    params[_("page")] = str(page_number)
    params.pop("_pjax", None)
    return "?{}".format(params.urlencode())


@register.simple_tag(takes_context=True)
def filter_build_params(context, key=None, value="", *exceptions):
    params = context["request"].GET.copy()
    for k in list(params):
        if k in ["o", "ot"] + list(exceptions):
            continue
        params.pop(k, None)
    if key:
        params[key] = value
    if len(params):
        return f"?{params.urlencode()}"
    return ""


@register.simple_tag(takes_context=True)
def filter_active(context, key=None, value="", return_value="active"):
    params = dict(context["request"].GET.lists())
    return return_value if str(value) in params.get(key, []) else ""


@register.simple_tag(takes_context=True)
def form_action_params(context, form, *args):
    # remove form fields from get parameters
    params = context["request"].GET.copy()
    params.pop("_pjax", None)

    for name, _field in form.fields.items():
        params.pop(form[name].html_name, None)
    for arg in args:
        params.pop(arg, None)
    return f"?{params.urlencode()}"


@register.filter
def has_filter_parameter(request):
    keys = set(key for key in request.GET if request.GET[key])
    return bool(keys.difference((_("page"),)))


@register.filter
@stringfilter
def replace(value, arg):
    if not isinstance(value, str) or value == "None":
        return ""

    if not isinstance(arg, str):
        return value

    try:
        search, replacer = arg.split(",", 1)
    except ValueError:
        return value

    return value.replace(search, replacer)


@register.filter
@stringfilter
def clean_url(value):
    if not isinstance(value, str) or value == "None":
        return ""
    scheme, netloc, path, params, query, fragment = urlparse(value)
    return "{}{}".format(netloc, path.split("/", 1)[0])


@register.filter
def trunc_number_with_dot(value, decimals=2):
    return decimal_filter(value, decimals, True)


@register.filter
def decimal_with_dot(value, decimals=2):
    return decimal_filter(value, decimals, False)


@register.filter(is_safe=True)
def priceformat(text, arg=-2) -> str:
    try:
        arg = int(arg)
    except (TypeError, ValueError):
        arg = -2

    result = floatformat(text, arg=arg)
    sep = get_format("DECIMAL_SEPARATOR")

    if result and arg <= 0:
        if sep not in result:
            result = "{}{}-".format(result, sep)
        elif result.endswith("{}00".format(sep)):
            result = "{}{}-".format(result.rsplit(sep, 1)[0], sep)

    if not result:
        return ""

    digits, decimals = result.rsplit(sep, 1)
    return "{}{}{}".format(intcomma(digits), sep, decimals)


@register.filter
@stringfilter
def deunicode(string):
    return strip_unicode(string)
