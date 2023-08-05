import unicodedata


def strip_unicode(string):
    string = string.replace("æ", "ae")
    string = string.replace("Æ", "AE")
    string = string.replace("œ", "oe")
    string = string.replace("Œ", "OE")
    string = string.replace("ø", "o")
    string = string.replace("Ø", "O")
    string = string.replace("ß", "ss")
    str_bytes = unicodedata.normalize("NFKD", string).encode("ascii", "ignore")
    return str_bytes.decode("ascii")
