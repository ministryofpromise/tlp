__author__ = "{ ministry of promise }"
__copyright__ = "Copyright 2015, { ministry of promise }"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Adam Nichols"
__email__ = "adam.j.nichols@gmail.com"
__status__ = "Development"

import re

regexs = {

    'ip': re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'),
    'domain': re.compile(r'^[a-zA-Z0-9\-\.]+\.(?![dll|exe|jar|asp|aspx|html|php|inf|bmp|gif])[a-zA-Z]{2,}$', re.I),
    'md5': re.compile(r'^[a-fA-F0-9]{32}$', re.I),
    'sha1': re.compile(r'^[a-fA-F0-9]{40}$', re.I),
    'sha256': re.compile(r'^[a-fA-F0-9]{64}$', re.I),
    'cve': re.compile(r'cve.+?\d{4}.+?\d{4}.*', re.I)

}
