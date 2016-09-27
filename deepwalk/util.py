import six
import chardet
from unicodedata import category
from datetime import date, datetime


def guess_encoding(text):
    if text is None or len(text) == 0:
        return
    if isinstance(text, unicode):
        return text
    enc = chardet.detect(text)
    out = enc.get('encoding', 'utf-8')
    if out is None:
        # Awkward!
        return text.decode('ascii', 'replace')
    return text.decode(out)


def string_value(value):
    """Brute-force convert a given object to a string.

    This will attempt an increasingly mean set of conversions to make a given
    object into a unicode string. It is guaranteed to either return unicode or
    None, if all conversions failed (or the value is indeed empty).
    """
    if value is None:
        return
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    elif isinstance(value, six.string_types):
        if not isinstance(value, six.text_type):
            enc = chardet.detect(value)
            enc = enc.get('encoding') or 'utf-8'
            value = value.decode(enc, 'replace')
        value = ''.join(ch for ch in value if category(ch)[0] != 'C')
        value = value.replace(u'\xfe\xff', '')  # remove BOM
        if not len(value.strip()):
            return
        return value
    else:
        value = unicode(value)
    return value
