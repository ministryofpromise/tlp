# tlp.py - threat language parser
#
# author: { ministry of promise }
# version: 0.1

# todo:
#
# - move to more sophisticated statistical model using histograms for keyword and phrase 
#   derivation
# - improve filter set
# - improve regex capabilities
# - use mozilla tld list to verify domain regex hits, removing ghetto file name matches


import nltk,re,operator,math,pprint
import numpy as np
from nltk.corpus import stopwords
from collections import Counter
from textblob import TextBlob
from lib.filter_list import ioc_blacklist as _ioc_blacklist
from lib.filter_list import keyword_blacklist as _keyword_blacklist
from lib.regex_list import regexs

class TLP:

    def __init__(self, raw_text=None, text_title=None):
        self._raw_text = raw_text
        self._text_title = text_title
        self._junk_list = self._get_junk_text()
        self._keywords = {"stats": {}, "keywords": set()}
        self._indicators = {"stats": {}, "indicators": set(), "cves": set()}
        if self._raw_text != None:
            self.blob = TextBlob(self._raw_text)

    
    # filter functions
    ############################################################################
    #
    # filter a list of words (words, tokens, iocs) against common terms or domains found
    # in threat data.

    def _filter_wordlist(self, wordlist):
        # set up filter criteria - we're using imports '_ioc_blacklist' and '_keyword_blacklist' as well
        # TODO: combine exports in smarter/more scalable way
        #       lemmatize keywords and blacklists for optimal matching

        stopword_blacklist = stopwords.words("english")
        blacklist = set(stopword_blacklist + _keyword_blacklist + _ioc_blacklist)
        #wordlist = [word.decode('utf8') for word in wordlist]
        return [word for word in wordlist if word not in blacklist]
    
   
    def _get_junk_text(self):
    
        # function to determine headers/footers/etc. and create list
        # to remove them from other text processing
    
        text = self._raw_text
        out = dict()
        for s in text.split('\n'):
            if len(s.split()) > 1:
                out[s.lower()] = out.get(s.lower(), 0) + 1

        junk_series = [v for (k,v) in out.iteritems() if v > 1]
        return [k for (k,v) in out.iteritems() if v > np.percentile(junk_series, 95)]


    def _filter_junk(self, input_list):
    
        # function will remove a word from a list if found in the junk_list of
        # headers and footer noise

        def check_current_term(term):
            for item in self._junk_list:
                if term in item:
                    return True

            return False

        output_list = []
        for item in input_list:
            if check_current_term(item):
                continue
            else:
                output_list.append(item)

        return output_list
 
    @property 
    def indicators(self):

        blob = self.blob.lower()
        for w in blob.words:
            for name,pattern in regexs.iteritems():
                if(re.match(pattern, w)):
                     self._indicators['stats'][name] = self._indicators['stats'].get(name, 0) + 1
                     self._indicators['indicators'].add(w)
        return self._indicators 

    @property 
    def summary(self):
    
        def nonalpha_median(blob):
            
            # returns median percentage of "junk" tokens in the blob
    
            sentences = blob.sentences
            nonalpha_ratios = []
            for s in sentences:
                tokens = s.tokens
                token_count = len(tokens)
                nonalpha_count = 0
                for token in tokens:
                    if not re.match('[a-zA-Z0-9]', token):
                        nonalpha_count += 1
        
                token_ratio = (float(nonalpha_count)/float(token_count)) * 100
                nonalpha_ratios.append(token_ratio)
        
            return(np.median(nonalpha_ratios))
        
        
        def nonalpha_pct(token_list):
        
            # trying to weed out garbage that isn't actual information, but tables of contents, appendixes,
            # and other non-sentence "sentences"
            #
            # return percentage of sentence that are non-alpha numeric, excluding anything non-english in the count
        
            nonalpha_count = 0
            for token in token_list:
                if not re.match('[a-zA-Z0-9]', token):
                    nonalpha_count += 1
        
            pct = (float(nonalpha_count)/float(len(token_list))) * 100
            return pct
        
    
        # process sentences in the doc to find a summary
        # count equivilent to first 10, or 3% of total sentences - whichever is fewer
    
        sentences = self.blob.sentences
        slen = len(sentences)
        third_pctl = math.floor(slen * .06)
        summ_len = third_pctl if third_pctl < 8 else 8
        counter = 0
    
        # iterate through sentences, weed out junk (tocs, indexes, appendicies, etc.)
        # stop appending when we reach desired len

        sentences_clean = []
        for s in sentences:
            if s.raw in self._junk_list:
                continue
            if nonalpha_pct(s.tokens) > nonalpha_median(self.blob):
                continue
            if len(s) >= 4:
                sentences_clean.append(s.raw)
            counter += 1
            if counter > summ_len:
                break
    
        # clean up what's left - no headers or other bs that textblob thinks constitute a sentence
        candidate =  " ".join(sentences_clean)
        candidate_lines = candidate.split('\n')
        summary = []
        for line in candidate_lines:
            words = line.split(' ')
            if not (re.search('\.$', line)) and (len(words) < 3):
                continue
    
            summary.append(line)
    
        # build a legible summary and return
        return " ".join(summary)
    

    @property
    def keywords(self):

        keywords = [word.lower() for word in self.blob.words]
        keywords_counted = Counter(keywords)
        
        total_count = 0
        keywords_dict = dict()
        for word, count in keywords_counted.iteritems():
    
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

        #bins = 3.5 * 0.96 * keywords_std * keywords_count ** (-1/3)
        #bins = np.sqrt(keywords_count)
        #(b, d) = np.histogram(keyword_scores, bins=bins)
        #pprint.pprint(zip(b.tolist(), d.tolist()))

        bins = np.log2(keywords_count) + 1
        (b, d) = np.histogram(keyword_scores, bins=bins)
        #pprint.pprint(zip(b.tolist(), d.tolist()))

        self._keywords['stats']['keywords_total'] = sum(keyword_scores)
        self._keywords['stats']['keywords_mean'] = keywords_mean
        self._keywords['stats']['keywords_std'] = keywords_std
        
        new_dict = dict([(k,v) for (k,v) in keywords_dict.iteritems() if v > (keywords_mean + (keywords_std * 2))])
        popular_keywords = sorted(new_dict.items(), key=operator.itemgetter(1), reverse = True)
        filtered_keywords = self._filter_junk([k for (k,v) in popular_keywords])
        self._keywords['keywords'] |= set(self._filter_wordlist([k for k in filtered_keywords])[:15])

    #def get_phrases(self):

        phrases = self.blob.noun_phrases
        phrases_counted = Counter(phrases)
        phrase_scores = [v for (k,v) in phrases_counted.iteritems()]
        phrases_mean = np.mean(phrase_scores)
        phrases_std = np.std(phrase_scores)

        # save as class var for later
        self._keywords['stats']['phrases_total'] = sum(phrase_scores)
        self._keywords['stats']['phrases_mean'] = phrases_mean
        self._keywords['stats']['phrases_std'] = phrases_std

        phrases_top = [(k,v) for (k,v) in phrases_counted.iteritems() if v > (phrases_mean + (phrases_std * 2))]
        self._keywords['keywords'] |= set(self._filter_wordlist(self._filter_junk([k for (k,v) in phrases_top])))
        return self._keywords
