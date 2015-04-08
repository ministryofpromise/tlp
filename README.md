# threat language parser

tlp is a python library that parses a body of text for indicators of compromise (iocs), leveraging the amazing [textblob](http://textblob.readthedocs.org/en/dev/) and [nltk](http://www.nltk.org/) natural language processing modules to derive context and color around those iocs.  The goal of tlp is to allow security analysts and researchers to extract and store meaningful data from the endless stream of information they encounter daily, without the tedium of endless ctrl+c, ctrl+v workflow.

To solve this problem, tlp uses a combination of regular expression, part-of-speech tagging, list filters, and simple statistical analysis to extract the following data from narritive-style prose:

- document summary
- indicators of compromise, with associated stats
- key words and phrases, with associated stats
- parser debugging information

## Installation

tlp uses setuptools, so installation of the module is as easy as cloning into it, and running:

    $ setup.py
    
## Dependencies

The following modules are required for tlp to function:

### TextBlob
TextBlob will be installed by nlp by default.  if you need to install manually, run:

        $ pip install -U textblob

After installing, you'll need to download and install the rest of the nltk corpora by running the following command:

        $ python -m textblob.download_corpora
    
### numpy   
Note that most numpy installs require compilation, so you will probably have to install this as a standalone by running:

        $ pip install -U numpy
        
## Usage

        >>> from tlp import TLP
        >>> ...
        >>> threat_text = get_threat_data_from_something()
        >>> tlp = TLP(threat_text)
        >>> # get summary
        >>> tlp.summary
        u"This report outlines a terrible scourge upon our internets: miscreants.
        ...
        Let's explore how we've punched them repeatedly with our data."
        >>> # get keywords, including calculation stats
        >>> tlp.keywords
        {
          'keywords': set([
                  u'miscreant', 
                  u'punch', 
                  u'scotch whiskey'
                  ]),
          'stats': {
                  'keywords_std': 6.4930233110851798, 
                  'keywords_mean': 3.227953410981697, 
                  'phrases_mean': 1.5883905013192612, 
                  'phrases_total': 1204, 
                  'keywords_total': 1940, 
                  'phrases_std': 3.1767579921851676
                  }
        }
        >>> # get indicators
        >>> tlp.indicators
        {
            'indicators': set([
                      u'miscreantsmustsuffer.com', 
                      u'8.8.4.4',
                      u'ministryofpromise.co.uk', 
                      u'127.0.0.1'
                      ]), 
            'stats': {
                    'ip': 2, 
                    'domain': 2, 
                    'cves': 3
                    }, 
            'cves': set([
                      u'cve-2011-0611', 
                      u'cve-2013-1347', 
                      u'cve-2013-2465'
                      ])
            }
        

## Contributing
We welcome any contributions to improve the code.  This is very much an alpha's alpha, so we expect many smart people will quickly spot inefficiencies or better ways to solve the problem.  All pull requests are welcome.

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
