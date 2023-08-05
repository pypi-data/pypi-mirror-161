from decimal import Decimal


def decimal_filter(value: [int, str, Decimal], decimals: int, truncate=False):
    if value is None:
        return ""

    if isinstance(value, str):
        if value == "":
            return ""

        value = value.replace(",", ".")
        try:
            value = float(value)
        except (TypeError, ValueError):
            return ""

    if isinstance(value, int) or isinstance(value, float):
        value = Decimal("{:.12f}".format(value))

    if isinstance(value, Decimal):
        if value == value.to_integral():
            value = value.quantize(Decimal(1))
        else:
            value = value.normalize()

        if not decimals:
            return str(value)

        dec = abs(value.as_tuple().exponent)
        if not truncate:
            dec = dec if dec > decimals else decimals
        else:
            dec = decimals + 2

        value = "{value:.{count}f}".format(value=value, count=dec)

        numb, dec = value.split(".")
        if len(dec) > decimals and not truncate:
            decimals = len(dec)
        dec = dec[:decimals]
        return "{numb}.{dec:0<{decimal_count}}".format(
            numb=numb, dec=dec, decimal_count=decimals
        )

    return str(value)
