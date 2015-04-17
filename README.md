# threat language parser

tlp is a python library that parses a body of text for indicators of compromise (iocs), leveraging the amazing [textblob](http://textblob.readthedocs.org/en/dev/) and [nltk](http://www.nltk.org/) natural language processing modules to derive context and color around those iocs.  The goal of tlp is to allow security analysts and researchers to extract and store meaningful data from the endless stream of information they encounter daily, without the tedium of endless ctrl+c, ctrl+v workflow.

To solve this problem, tlp uses a combination of regular expression, part-of-speech tagging, list filters, and simple statistical analysis to extract the following data from narritive-style prose:

- document summary
- indicators of compromise, with associated stats
- key words and phrases, with associated stats
- parser debugging information

## Installation

tlp can be found on PyPi, and installed with:
    
    $ pip install tlp

you are also able to clone this repo, and run:

    $ python setup.py install
    
## Dependencies

The following modules are required for tlp to function:

### TextBlob
TextBlob will be installed by default.  if you need to install manually, run:

        $ pip install -U textblob

*PLEASE NOTE:* Regardless of whether TextBlob is automatically or manually installed, you'll need to download and install the rest of the nltk corpora by running the following command:

        $ python -m textblob.download_corpora
    
### numpy   
Note that most numpy installs require compilation, so you will probably have to install this as a standalone by running:

        $ pip install -U numpy
        
### python-Levenshtein
This dependency should be installed by setuptools automatically, but in the event that fails:

        $ pip install -U python-Levenshtein
        
## Usage

        >>> from tlp import TLP
        >>> ...
        >>> threat_text = get_threat_data_from_something()
        >>> tlp = TLP(threat_text)
        >>>
        >>> # get summary
        >>> tlp.summary
        u"This report outlines a terrible scourge upon our internets: miscreants. We have
        discovered that miscreants are systematically taking over the series of tubes, and
        and are attempting to leverage them to proliferate their love of 'My Little Pony.' 
        Let's explore how we punched them repeatedly with our data."
        >>>
        >>> # get keywords, occurance counts
        >>> tlp.keywords
        [
            (u'miscreant', 97), 
            (u'punch', 39), 
            (u'whiskey', 18)
        ]
        >>>
        >>> # get iocs, sorted by type
        >>> tlp.iocs
        {
            'cve': set([u'cve-2011-0611', 
                        u'cve-2013-1347', 
                        u'cve-2013-2465']),
            'domain': set([u'miscreantsmustsuffer.com',
                           u'ministryofpromise.co.uk']),
            'ip': set([u'8.8.4.4',
                       u'127.0.0.1']),
            'md5': set([u'6fc67ebcb6423efa06198cd123ffc3ee']),
            'sha1': set([]),
            'sha256': set([])
        }
        >>>
        >>> # get tlp color (if present)
        >>> tlp.color
        set([u'white'])
        >>>
        >>> # get debug info, including total word count, and word frequency mean/stddev
        >>> tlp.debug
        {
            'keywords': {
                'std': 2.5559937998299809, 
                'total': 1012, 
                'mean': 2.0321285140562249
            }, 
            'iocs': {
                'ip': 2,
                'domain': 2, 
                'md5': 1
                'sha1': 0,
                'sha256': 0,
                'cve': 3
            }
        }
        >>>
        >>> # get complete filtered text used for data distillation 
        >>> tlp.text
        u"This report outlines a terrible scourge upon our internets: miscreants. We have
        discovered that miscreants are systematically taking over the series of tubes, and
        and are attempting to leverage them to proliferate their love of 'My Little Pony.' 
        Let's explore how we punched them repeatedly with our data.
        ...
        
        "In conclusion -- bottom's up!"
        

## Todo

- Improve keyword accuracy with a more robust statistical approach and better contextual language processing
- Modify ioc filter engine to allow for more modular filter management
- Allow for more flexibility in parsing and filtering at object creation 
- Grow/improve regex and filter sets
- Include the use of "title" __init__ arg in keyword weighting

## Contributing
This is very much an alpha, so we expect some folks will quickly spot inefficiencies or better ways to solve the problem.  All pull requests are welcome. :)

If you are a threat intelligence publisher who would like to be added to the tlp whitelist, please [contact](mailto:github@ministryofpromise.co.uk) us.

## License
The MIT License (MIT)

Copyright (c) 2015 { ministry of promise }

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
