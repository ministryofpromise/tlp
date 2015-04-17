#!/usr/bin/env python

'''
tlp is a python library that parses a body of text for indicators of compromise (iocs), 
leveraging the amazing textblob and nltk natural language processing modules to derive 
context and color around those iocs. 
'''

from textblob import TextBlob
from textblob import Sentence
from textblob import WordList
from textblob import Word
from nltk.corpus import stopwords as sw
from collections import Counter
from Levenshtein import distance
from lib.filter_list import *
from pkg_resources import resource_filename, Requirement
import numpy as np
import types,re,operator,codecs

__author__ = "{ ministry of promise }"
__copyright__ = "Copyright 2015, { ministry of promise }"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Adam Nichols"
__email__ = "adam.j.nichols@gmail.com"
__status__ = "Development"

class TLPFilter:

    def __init__(self, user_filterlist=None):

        try:
            # initialize some junk
            self.user_filterlist = None
            self.ubl_file_obj = None
            self.global_filterlist = list()

            # check for filterlist, handle accordingly

            if user_filterlist is not None:

                self.user_filterlist = user_filterlist

                if type(self.user_filterlist) is list:
                    pass
                elif type(self.user_filterlist) is str:
                    self.ubl_file_obj = open(self.user_filterlist, "r")
                    for line in self.ubl_file_obj.readlines():
                        if re.match('^#', line):
                            continue
                        self.global_filterlist.append(unicode(line.strip().lower()))
                        #self.global_filterlist + keyword_filterlist
                else:
                    raise ValueError("supplied blacklist is not of type <str> or <list>")

        except Exception as e:
            raise e


    '''
    utility functions
    
    misc. stuff used elsewhere:
            - nonalpha_pct: function to determine the ratio of non-alpha tokens in a sentence
            - nonalpha_thresh: analyzes each sentence in a blob and derives the threshold  
              ratio of junk tokens per sentence.
            - moz_tlds: return a list of tlds from the mozilla project tld list 
              maintained at https://publicsuffix.org/list/effective_tld_names.dat
    '''

    def nonalpha_pct(self, sentence):

        try:
            # TODO - NASTY HACK
            if len(sentence) == 0:
                return 1
            tokens = sentence.tokens
            nonalpha_count = 0
            for token in tokens:
                if not re.search('[a-zA-Z0-9]+', token):
                    nonalpha_count += 1
        
            return (float(nonalpha_count)/float(len(tokens))) * 100

        except Exception as e:
            raise e


    def nonalpha_thresh(self, blob):

        try:
            sentences = blob.sentences
            nonalpha_ratios = []
            for s in sentences:
                nonalpha_ratios.append(self.nonalpha_pct(s))

            return(np.median(nonalpha_ratios) + (np.std(nonalpha_ratios) * 3))

        except Exception as e:
            raise e


    def moz_tlds(self):

        try:
            effective_tld_names = resource_filename(Requirement.parse('tlp'), 'tlp/lib/effective_tld_names.dat')
            f = codecs.open(effective_tld_names, 'r', 'utf-8')
            moz_tlds = f.readlines()
            moz_tlds = [item.strip() for item in moz_tlds if not (re.match('^//', item) or re.match('^$', item))]
    
            return moz_tlds

        except Exception as e:
            raise e

    ''' 
    filter functions
     
    take the TextBlob primative types (sentences, words, tokens) and clean them through the removal or normalization of:
            - items without punctuation
            - items with titlized capitalization
            - "sentences" that contain newlines (how to seperate junk from poorly formatted content?)
            - repeated sentences
            - headers/footers/content section labels
            - items with a high punctuation, or "junk" ratio (ToCs, page numbers, etc)

    each function in this section should produce output for itself, as well as adding to the global blacklist of items 
    that should be removed from the statistical analysis of text to produce summary and keywords.
    '''

    def text(self, text):

        try:
            # check for text, transform to unicode if necessary 
            if text is not None:
                if not (type(text) is unicode or type(text) is str):
                    raise TypeError("supplied text object of type that is not str or unicode")
                else:
                    if not type(text) is unicode:
                        text = text.decode('utf8')
    
                    # unicode?  unicode.
                    blob = TextBlob(text)
                    blob_nonalpha_thresh = self.nonalpha_thresh(blob)
            else:
                raise ValueError("no input text supplied")
             
                   
            # replace all instances of sentences broken by newline
            # to ensure that we're dealing with contiguous text 
    
            s1_text = re.sub(r'([a-z\,]+)[\n\r]+?([^A-Z0-9]+?)', r'\1 \2', text)
            s1_list = list()
    
            # try to remove header-type section labels through the use of some convoluted
            # rule bs.  really not elegant, but it works.
         
            stopwords = sw.words("english")
            for sentence in s1_text.split('\n'):
                # line begins or ends with a number - maybe ToC or heading
                if re.match('(?:^[0-9]+?|[0-9]+?[\n\r]+?$)', sentence):
                    continue
                words = sentence.split()   
                if len(words) <= 3:
                    continue
                for word in words:
                    # boring word
                    if word.lower() in stopwords:
                        continue
                    # not a word - unicode bullets or other nonsense
                    if not re.match(r'\w+?', word):
                        continue
                    # links
                    if re.match(r'^[a-zA-Z]+\:\/\/', word):
                        continue
                    # no title case headings
                    if not re.match('^[0-9A-Z]{1}', word):
                        s1_list.append(sentence)
                        break
    
            # let's clear out anything with a nonalpha token ratio higher than the threshold
            
            s2_list = [s for s in s1_list if self.nonalpha_pct(Sentence(s)) < (len(s)/4)]
                    
            # now that we've got a semi-clean set of data, we can do some statistical analysis
            # to determine if we've got a lot of repeat data like headers/footers/copyrights
            # that can skew our keyword stats
    
            sentence_counts = Counter(s2_list) 
            sc_series = [v for (k,v) in sentence_counts.iteritems()] 
            sc_std = np.std(sc_series)
            sc_median = np.median(sc_series)
    
            # if we have repeating text, rebuilt it minus that noise, or anything
            # specified in the global blacklist
    
            if sc_median >= 1:
                final_list = []
    
                # some edge cases force us to break outlier "sentences" into smaller units 
                # for comparison later
                # 
                # once the list is built, we have to check a few different ways to ensure 
                # we are removing all the noise we can
    
                sentence_outliers = [k.strip().lower() for (k,v) in sentence_counts.iteritems() if v >= (sc_median + (sc_std * 2)) > 1]
                self.global_filterlist += sentence_outliers
                for s in s2_list:
                    if s.lower() in self.global_filterlist:
                        continue
                    for o in sentence_outliers:
                        if distance(o, s.lower()) < float(len(s) * .35):
                            break
                        elif o in s.lower():
                            break
                    else:
                        final_list.append(s)
    
            # text had no repeats or noise to filter (rare)
            else:
                final_list = s2_list
    
            # we out
            return " ".join(final_list)

        except Exception as e:
            raise e


    def keywords(self, keywords):

        try:
            if keywords is not None:
                if not (isinstance(keywords, list) or isinstance(keywords, WordList)):
                    raise TypeError('supplied keyword object of type that is not list or TextBlob.WordList')
                else:
                    if isinstance(keywords, list):
                        keywords = [Word(word.lower()) for word in keywords]
            else:
                raise ValueError('no input keywords supplied')
    
            # normalize case
            words = [word.lower() for word in keywords]
    
            # remove all stopwords
            stopwords = sw.words("english")
            words = [word for word in words if word not in stopwords] 
            #words = [word for word in keywords] 
            nwords = []
            for word in words:
                if word in keyword_filterlist:
                #if word.string in keyword_filterlist:
                    continue
                for term in self.global_filterlist:
                    #if word.string in term:
                    if word in term:
                        pass
                        #break
                else:
                    nwords.append(word)
    
            # remove plural, reduce to stems
            # textblob breaks possessives and other contractions into 
            # two distinct words, but sometimes leaves a trailing unicode 
            # apostrophe - if so, strip it
    
            words = [word.strip(u'\u2019') for word in nwords]
    
            return words

        except Exception as e:
            raise e


    def iocs(self, data, mode):

        try:
            if not (mode == 'pre' or mode == 'post'):
                raise ValueError('invalid mode specified')
    
            # pre-filter to clean raw text for optimal ioc parsing
            if mode == 'pre':
    
                if not data or type(data) is not unicode:
                    raise ValueError('invalid data supplied')
    
                # stupid "object replacement character" -- essentially a utf space
                data = [re.sub(ur'\uFFFC+', ' ', w) for w in data]
                data = [re.sub(ur'[\s\t\n\r]', ' ', w) for w in data]
                data = "".join(data).split(' ')
    
                return data
    
            # post-filter to remove good sites, and other blacklisted iocs
            if mode == 'post':
    
                if not type(data) is dict or data is None:
                    raise ValueError('invalid data supplied')
        
                # filter domain
                moz_tlds = self.moz_tlds()
                for ioc in data['domain'].copy():
                    filterlist = alexa_filterlist + ioc_filterlist['domain']
                    for domain in filterlist:
                        re_match = ur'.*' + re.escape(domain) + '$'
                        if re.match(re_match, ioc):
                            data['domain'].remove(ioc)
                            break
    
                    for tld in moz_tlds:
                        re_match = ur'.*\.?' + re.escape(tld) + '$'
                        if re.match(re_match, ioc):
                            break
                    else:
                        data['domain'].remove(ioc)

                # filter ip
                for ioc in data['ip'].copy():
                    filterlist = ioc_filterlist['ip']
                    if ioc in filterlist:
                        data['ip'].remove(ioc)     
    
                return data

        except Exception as e:
            raise e
