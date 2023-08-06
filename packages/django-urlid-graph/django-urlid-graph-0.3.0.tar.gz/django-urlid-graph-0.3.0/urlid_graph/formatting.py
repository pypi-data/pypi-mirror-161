import re
from datetime import date, datetime

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import date as django_date

REGEXP_NOT_NUMBERS = re.compile("[^0-9*]")


def convert_date(value):
    if isinstance(value, str):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def convert_datetime(value):
    if isinstance(value, str):
        return value
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def convert_bool(value):
    return bool(int(value))


def format_cnpj(value):
    value = (value or "").strip()
    if not value:
        return None
    value = f"{int(REGEXP_NOT_NUMBERS.sub('', value)):014d}"

    return f"{value[:2]}.{value[2:5]}.{value[5:8]}/{value[8:12]}-{value[12:14]}"


def format_cpf(value):
    value = (value or "").strip()
    if not value:
        return None
    value = REGEXP_NOT_NUMBERS.sub("", value)
    if "*" not in value:
        value = f"{int(value):011d}"
    elif len(value) < 11:
        value = "0" * (11 - len(value)) + value

    return f"{value[:3]}.{value[3:6]}.{value[6:9]}-{value[9:11]}"


def format_titulo_eleitoral(value):
    value = (value or "").strip()
    if not value:
        return None
    value = f"{int(REGEXP_NOT_NUMBERS.sub('', value)):012d}"

    return f"{value[:4]}.{value[4:8]}.{value[8:10]}-{value[10:12]}"


def format_property_value(name, label, value):
    if isinstance(value, datetime):
        return django_date(value, settings.DATETIME_FORMAT)
    elif isinstance(value, date):
        return django_date(value, settings.DATE_FORMAT)
    elif name == "cnpj":
        return format_cnpj(value)
    elif name.startswith("cpf"):
        return format_cpf(value)
    elif name == "titulo_eleitoral":
        return format_titulo_eleitoral(value)
    elif name == "numero_sequencial":
        return intcomma(value)
    else:
        return value


def format_unknown_property_value(name, label, value):
    value = format_property_value(name, label, value)

    # Edges properties don't have an explicit value type, so we have to infer
    # for dates format
    try:
        value = convert_datetime(value)
        value = django_date(value, settings.DATETIME_FORMAT)
    except (TypeError, ValueError):
        try:
            value = convert_date(value)
            value = django_date(value, settings.DATE_FORMAT)
        except (TypeError, ValueError):
            pass
    return value
