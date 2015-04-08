import re

regexs = {

    'ip': re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'),
    'domain': re.compile(r'^[a-zA-Z0-9\-\.]+\.(?![dll|exe|jar|asp|aspx|html|php|inf])[a-zA-Z]{2,}$', re.I),
    'md5': re.compile(r'^[a-fA-F0-9]{32}$', re.I),
    'sha1': re.compile(r'^[a-fA-F0-9]{40}$', re.I),
    'sha256': re.compile(r'^[a-fA-F0-9]{64}$', re.I),
    'cves': re.compile(r'cve.+?\d{4}.+?\d{4}.*', re.I)

}
