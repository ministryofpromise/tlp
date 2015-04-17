#!/usr/bin/env python

'''
tlp is a python library that parses a body of text for indicators of compromise (iocs), 
leveraging the amazing textblob and nltk natural language processing modules to derive 
context and color around those iocs. 
'''

import nltk,re,operator,math,pprint
import numpy as np
from tlp_filter import TLPFilter
from nltk.corpus import stopwords
from nltk.util import ngrams
from collections import Counter
from textblob import TextBlob
from lib.regex_list import regexs

__author__ = "{ ministry of promise }"
__copyright__ = "Copyright 2015, { ministry of promise }"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Adam Nichols"
__email__ = "adam.j.nichols@gmail.com"
__status__ = "Development"

class TLP:

    def __init__(self, raw_text=None, text_title=None):

        try:
            # props for internal use
            self._raw_text = raw_text
            self._text_title = text_title

            # props to store data
            self._summary = str()
            self._keywords = set()
            self._iocs = dict()
            self._tlp = None
            self._debug = dict({'iocs': dict(), 'keywords': dict()})

            if self._raw_text != None:
                if not type(self._raw_text) is unicode:
                    self._raw_text = self._raw_text.decode('utf8')
                self._tlpfilter = TLPFilter()
                self._clean_text = self._tlpfilter.text(self._raw_text)
                self._blob = TextBlob(self._raw_text)
                self._clean_blob = TextBlob(self._clean_text)

        except Exception as e:
            import traceback
            traceback.print_exc()


    @property 
    def iocs(self):
        '''returns a filtered list of iocs'''

        try:
            if len(self._iocs) > 0:
                return self._iocs
    
            # prime the dict
            self._iocs = dict((k, set()) for k in regexs)
            
            # parse iocs
            data = self._tlpfilter.iocs(self._raw_text, mode='pre')
            for w in data:
                # remove the neuter braces, if present
                re.sub(ur'[\[\]]+?', '', w)
                for name,pattern in regexs.iteritems():
                    if(re.match(pattern, w)):
                         self._iocs[name].add(w)
            self._iocs = self._tlpfilter.iocs(self._iocs, mode='post')
            for key in self._iocs:
                self._debug['iocs'][key] = len(self._iocs[key])
            return self._iocs

        except Exception as e:
            raise e


    @property
    def text(self):
        '''returns the complete filtered text'''

        try:
            return "  ".join([s.raw for s in self._clean_blob.sentences])

        except Exception as e:
            raise e


    @property
    def debug(self):
        '''returns debug info -  must run 'keywords' or 'iocs' to populate'''
        return self._debug


    @property 
    def summary(self):
        '''returns document summary'''

        try:
            if len(self._summary) > 0:
                return self._summary
            
            sentences = self._clean_blob.sentences
            slen = len(sentences)
            sixth_pctl = int(math.floor(slen * .06))
            if sixth_pctl < 8:
                summ_len = sixth_pctl if sixth_pctl > 2 else 2
            else:
                summ_len = 8
            
            return "  ".join([s.raw for s in sentences[:summ_len]])

        except Exception as e:
            raise e


    @property
    def color(self):
        '''returns tlp color (if present)'''

        try:
            bigrams = ngrams(self._raw_text.split(), 2)
            colors = set()
            for b in bigrams:
                (one, two) = b
                if re.search('(?:tlp|TLP)', one): 
                    colors.add(two.lower())
                
            return colors 

        except Exception as e:
            raise e

 
    @property
    def keywords(self):
        '''returns document keywords and occurance counts'''

        try:
            if len(self._keywords) > 0:
                return self._keywords
    
            #blob = TextBlob(self.summary)
            blob = TextBlob(self._clean_text)
            keywords = self._blob.words
            keywords = self._tlpfilter.keywords(keywords)
            keywords_counted = dict(Counter(keywords))
            total_count = 0
            keywords_dict = dict()
            for word, count in keywords_counted.iteritems():
    
                if len(word) == 0:
                    continue
        
                # you're certainly not popular if you only occur once
                # if you are popular, and you're longer than 3 chars, you win
    
                total_count += count if count > 1 else 0
                pos_array = nltk.pos_tag(nltk.word_tokenize(word))
                w,pos = pos_array[0]
                if re.search('.*[NN|NP]$', pos):
                    if len(w) > 3:
                        keywords_dict[word] = count 
            
            keyword_scores = [v for (k,v) in keywords_dict.iteritems()]
            keywords_count = np.count_nonzero(keyword_scores)
            keywords_mean = np.mean(keyword_scores)
            keywords_std = np.std(keyword_scores)
    
            self._debug['keywords']['total'] = sum(keyword_scores)
            self._debug['keywords']['mean'] = keywords_mean
            self._debug['keywords']['std'] = keywords_std
            
            new_dict = dict([(k,v) for (k,v) in keywords_dict.iteritems() if v > (keywords_mean + (keywords_std * 4))])
            self._keywords = sorted(new_dict.items(), key=operator.itemgetter(1), reverse = True)
    
            return self._keywords
            
        except Exception as e:
            raise e
