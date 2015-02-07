import io
import sys

if sys.version_info[0] < 3:
    NativeStream = io.BytesIO
else:   #pragma: NO COVER Py3k
    NativeStream = io.StringIO

try:
    from urllib import quote
except:  # pragma: NO COVER Py3k
    from urllib.parse import quote

try:
    from urlparse import parse_qsl
except:   #pragma: NO COVER Py3k
    from urllib.parse import parse_qsl
