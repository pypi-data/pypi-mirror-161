# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 09:19:53 2021

@author: gg646
"""

# import numpy as np
import string
import os
import nltk
import gensim
import re
import spacy
from bs4 import BeautifulSoup  # Web page parsing and data acquisition
import re  # Regular expressions for text matching
import urllib.request, urllib.error  # Make URL and get web page data
import scispacy
import en_ner_bc5cdr_md
import pandas as pd
import xml.etree.ElementTree as ET
from nltk.tokenize import word_tokenize
from gensim.corpora.dictionary import Dictionary
from nltk.stem import WordNetLemmatizer, SnowballStemmer
import matplotlib.pyplot as plt
Important_sections = ['ABSTRACT', 'INTRO', 'METHODS', 'DISCUSS', 'RESULTS', 'CASE', 'CONCL', 'ABBR', 'FIG', 'TABLE']
Other_sections = ['SUPPL', 'REF', 'APPENDIX', 'AUTH_CONT', 'ACK_FUND', 'COMP_INT', 'REVIEW_INFO']

stpwrd = nltk.corpus.stopwords.words('english')

# Adding new stop words to the list of stop words:
new_stopwords = ["surname", "ref", "abstract", "intro", "http", 'left upper', 'right upper', 'article',
                 'published', 'even though', 'paragraph', 'page', 'sentence', 'et', 'al', 'etc']
stpwrd.extend(new_stopwords)

wrong_entities = ['PD', 'HSV-1', 'SNpc', 'anti-MAG', 'anti-ACE', 'AG129', 'Campylobacter', 'Mycoplasma', 'GB',
                  'Bickerstaff',
                  'Abbott', 'CR', 'Casa', 'Cc', 'DSB', 'Corona', 'DR', 'Ebola', 'pp1a', 'Ruminococcus', 'Bloom',
                  'Communicate',
                  'Diamond', 'Sulistio', 'Underwood', 'Kanduc', 'NetMHCpan', 'Pairing',
                  'S Surface', 'Acute', 'Articles', 'Hospital', 'Inclusion', 'Pneumonia', 'Prothrombin', 'Tumor',
                  'Anesthesia', 'Cronbach', 'RM', 'E3', 'ER', 'N', "N636'-Q653", "N638'-R652", 'PIKfyve',
                  'Phase II', 'SB', 'Criteria', 'M.H.', 'Outcomes', 'pH', 'Dyspnea', 'TRIzol', 'Postoperative',
                  'Moderna',
                  'Gardasil', 'BioNTech', 'Inhibits', 'Figure', 'States', 'Eq', 'Nor-diazepam,-{N',
                  'Nor-diazepam,-{N-hydroxymethyl}aminocarbonyloxy',
                  'who´ve', '-CoV-', 'Kingdom', 'Nterminal', 'Wellbeing Note', 'TiTiTx', 'casesProtocol', 'Medicineof',
                  'Aviso', 'Iranto', 'BrazilJune', 'Xray', 'Xrays', 'Xraysuse', 'Homebased', 'Phase', 'Vaccinia',
                  'Dlaptop'
                  ]

xml_papers =['PMC6988271.xml']
# xml_papers =['desktop.ini', 'PMC6988269.xml', 'PMC6988271.xml', 'PMC6988272.xml', 'PMC6995816.xml', 'PMC7001239.xml', 'PMC7001240.xml', 'PMC7003341.xml', 'PMC7004396.xml', 'PMC7008072.xml', 'PMC7008073.xml', 'PMC7011107.xml', 'PMC7014668.xml', 'PMC7014669.xml', 'PMC7014672.xml', 'PMC7017878.xml', 'PMC7017962.xml', 'PMC7019868.xml', 'PMC7025910.xml', 'PMC7026896.xml', 'PMC7029158.xml', 'PMC7029402.xml', 'PMC7029448.xml', 'PMC7029449.xml']
if "desktop.ini" in xml_papers:
    xml_papers.remove("desktop.ini")
x=0
for i in xml_papers:
    xml_papers[x]=i.replace('.xml','')
    xml_papers[x] = xml_papers[x].replace('PMC', '')
    x+=1

docs1 = dict.fromkeys(xml_papers)
articles = [[] for i in range(len(xml_papers))]
# Making a list of files names in rootpath
baseurl = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/PMC"
addurl= "/unicode"
# for html.............................................................................forhtml#
# for html.............................................................................forhtml#
# for html.............................................................................forhtml#
def askURL(url):
    head = {  # Simulate browser header information
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"
    }


    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html

def To_Generate_Key_Word(number):
    number
    myinput =str(number)
    url = baseurl+str(myinput)+addurl
    html = askURL(url)  # Save the obtained web page source code
    # 2.Parse data one by one
    soup = BeautifulSoup(html, "html.parser")
    soup=str(soup)
    collection=ET.XML(soup)
    numm=str("PMC"+myinput)

    # will contain articles after parsing

    Other_sections = ['SUPPL', 'REF', 'APPENDIX', 'AUTH_CONT', 'ACK_FUND', 'COMP_INT', 'REVIEW_INFO']


    section_types1 = {}
    xml_papers.append(myinput)
    for k, article in enumerate(xml_papers):
        url = baseurl + str(article) + addurl
        html = askURL(url)  # Save the obtained web page source code
        # 2.Parse data one by one
        soup1 = BeautifulSoup(html, "html.parser")
        soup1 = str(soup1)
        collection1 = ET.XML(soup1)
        section_types1[xml_papers[k]] = []
        docs1[xml_papers[k]] = []

        # Extracting all the texts of all sections
        for i, document in enumerate(collection1):

            for x in document.findall("passage"):
                # print(x.findall('infon'))
                infon_list = x.findall('infon')

                # Removing footnote and table contents sections:
                if any(inf.text == 'footnote' for inf in infon_list) or any(inf.text == 'table' for inf in infon_list):
                    document.remove(x)

            for x in document.findall("passage"):
                for inf in x.findall('infon'):
                    if inf.attrib == {'key': 'section_type'}:
                        section_types1[xml_papers[k]].append(inf.text)
                        if inf.text not in Other_sections:
                            temp1 = getattr(x.find('text'), 'text', None)
                            if inf.text in ['ABSTRACT', 'CONCL']:
                                docs1[xml_papers[k]].append(temp1
                                                            )
                            else:
                                docs1[xml_papers[k]].append(temp1)

        docs1[xml_papers[k]] = list(filter(None, docs1[xml_papers[k]]))
    docs_list1 = [' '.join(docs1.get(doc)) for doc in docs1]

    # for html.............................................................................forhtml#
    # for html.............................................................................forhtml#
    # for html.............................................................................forhtml#


    # part1.............................................................................part1#
    # part1.............................................................................part1#
    # part1.............................................................................part1#
    data_for_mianWorld = [re.sub(r'\s', ' ', doc) for doc in docs_list1]
    # removing urls:
    # https:\/\/www\.\w+\.\w+
    data_for_mianWorld = [re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', ' ', doc) for doc in data_for_mianWorld]
    # removing numbers
    # r'[\s\(][^-a-zA-Z]+\-*[\d\.]+'
    data_for_mianWorld = [re.sub(r'[\s\(][^-a-zA-Z]+\-*[^-a-zA-Z]+', ' ', doc) for doc in data_for_mianWorld]
    # Adding 2019 to -nCoV:
    data_for_mianWorld = [re.sub(r'-nCoV', '2019-nCoV', doc) for doc in data_for_mianWorld]
    # Removing medical units:
    data_for_mianWorld = [re.sub(r'[a-zA-Z]+\/[a-zA-Z]+', '', doc) for doc in data_for_mianWorld]
    # Removing white spaces again
    data_for_mianWorld = [re.sub(r'\s', ' ', doc) for doc in data_for_mianWorld]
    # removing punctuations:
    # removing '-' from punctuations list.
    punctuation = '!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'
    data_for_mianWorld = [re.sub(r'[{}]+'.format(punctuation), '', doc) for doc in data_for_mianWorld]
    pattern = r'[A-Z]{1}[a-z]{2,}\s'
    for i, doc in enumerate(data_for_mianWorld):
        index_temp = [(m.start(0), m.end(0)) for m in re.finditer(pattern, doc)]
        for ind in index_temp:
            ii = ind[0]
            jj = ind[1]
            data_for_mianWorld[i] = data_for_mianWorld[i].replace(data_for_mianWorld[i][ii:jj], data_for_mianWorld[i][ii:jj].lower())
    stemmer = SnowballStemmer("english")
    wnl = WordNetLemmatizer()


    # A function for lemmatizing and stemming a text
    def lemmatize_stemming(text):
        return stemmer.stem(wnl.lemmatize(text, pos='v'))


    # A token preprocessing function
    def preprocess(text):
        result = []
        mydict = {}  # A dictionary which will contain original tokens before lemmatizing and stemming
        for token in word_tokenize(text):
            # if token not in stpwrd and len(token) >= 3:
            if len(token) >= 2:
                temp = lemmatize_stemming(token)
                mydict[temp] = token
                result.append(temp)
        return result, mydict


    mywords = []
    # A dictionary which contains original tokens as value and lemmetized stemmized token as key:
    token_word_dict = {}

    for doc in data_for_mianWorld:
        # print(preprocess(doc)[0])
        mywords.append(preprocess(doc)[0])
        token_word_dict.update(preprocess(doc)[1])
        # print(preprocess(doc)[1])

    # Removing words with frequency < 2:
    for sub in mywords:
        sub[:] = [ele for ele in sub if sub.count(ele) > 1]

    # Building the bigram models
    bigram = gensim.models.phrases.Phrases(mywords, min_count=2, threshold=10)

    # cearting list of bigrams:
    mywords2 = bigram[mywords]

    # Building the trigram models
    trigram = gensim.models.phrases.Phrases(bigram[mywords], min_count=2, threshold=10)
    mywords3 = trigram[mywords2]


    # A function for removing stop words:
    def remove_stopwrd(txt):
        result = []
        for wrd in txt:
            temp = wrd.split('_')
            if not any(ele in stpwrd for ele in temp):
                result.append(wrd)
        return result


    mywords3_no_stopwrd = [[] for i in range(len(mywords3))]

    mywords3_no_stopwrd = [remove_stopwrd(lis) for lis in mywords3]
    # Create Dictionary of trigrams
    dictionary_trigram = Dictionary(mywords3_no_stopwrd)

    # Create Corpus
    corpus_trigram = [dictionary_trigram.doc2bow(text) for text in mywords3_no_stopwrd]

    # =============================================================================

    tfidf_trigram_model = gensim.models.tfidfmodel.TfidfModel(corpus=corpus_trigram,
                                                              id2word=dictionary_trigram,
                                                              normalize=True)

    # Top 10 tokens
    # tfidf_top10_words=[[] for i in range(len(corpus_trigram))]
    top10_trigram_of_articles = [[] for i in range(len(corpus_trigram))]

    # Will contain the original words before being stemmized and lemmatized:
    top10_tri_words_original = [[] for i in range(len(corpus_trigram))]
    top10_tri_freqs = [[] for i in range(len(corpus_trigram))]

    for i, corp in enumerate(corpus_trigram):
        temp3 = tfidf_trigram_model[corp]
        # print(temp3)
        temp_top10 = sorted(temp3, key=lambda x: x[1], reverse=True)[:10]
        temp_top10_wrds = [dictionary_trigram.get(x[0]) for x in temp_top10]
        top10_trigram = [' '.join(re.findall(r'[\w\-]+\_[\w\-]+[\_[\w\-]+]*', word)) for word in temp_top10_wrds]
        top10_trigram_of_articles[i] = [' '.join(re.findall(r'[\w\-]+\_[\w\-]+[\_[\w\-]+]*', word)) for word in
                                        temp_top10_wrds]
        while ("" in top10_trigram):
            top10_trigram.remove("")
        temp4_top10words = [(dictionary_trigram.get(x[0]), x[1]) for x in temp_top10]
        # print (temp_top10)
        # print("---------------")
        # print(temp4_top10words)
        # print("---------------")

        # Finding the original words of top10 trigrams:
        # Getting the original words, Unstemming
        for m, n in temp4_top10words:
            if m in top10_trigram:
                temp5 = m.split('_')
                temp6 = ''
                for ii, tex in enumerate(temp5):  # Rejoining the trigrams with '_' again
                    temp6 = temp6 + token_word_dict.get(temp5[ii]) + '_'
                    # print(temp6)
                top10_tri_words_original[i].append(temp6)
                top10_tri_freqs[i].append(n)
                # print(m,n, temp6)
            else:
                top10_tri_words_original[i].append(token_word_dict.get(m))
                top10_tri_freqs[i].append(n)
                # print(m, n, token_word_dict.get(m))
    num = xml_papers.index(myinput)
    # plt.figure(figsize=(20, 3))  # width:20, height:3
    plt.bar(top10_tri_words_original[num], top10_tri_freqs[num])
    plt.title(f'Top 10 trigrams "weighted" for {xml_papers[num]}')
    plt.xticks(rotation=45, fontsize=11)
        # Saving the figures in result path:
    plt.savefig(f'Trigram_figure_{xml_papers[num]}', bbox_inches="tight")
    plt.close()

# part1.............................................................................part1#
# part1.............................................................................part1#
# part1.............................................................................part1#
# A dictionary that will contain section types of the articles
def To_Generate_Location(number):
    number
    myinput =str(number)
    url = baseurl+str(myinput)+addurl
    html = askURL(url)  # Save the obtained web page source code
    # 2.Parse data one by one
    soup = BeautifulSoup(html, "html.parser")
    soup=str(soup)
    collection=ET.XML(soup)
    numm=str("PMC"+myinput)

    section_types = {}
    docs={}
    section_types[numm] = []
    docs[numm] = []
    for i, document in enumerate(collection):

        for x in document.findall("passage"):
            # print(x.findall('infon'))
            infon_list = x.findall('infon')

            # Removing footnote and table contents sections:
            if any(inf.text == 'footnote' for inf in infon_list) or any(inf.text == 'table' for inf in infon_list):
                document.remove(x)

        for x in document.findall("passage"):
            for inf in x.findall('infon'):
                if inf.attrib == {'key': 'section_type'}:
                    section_types[numm].append(inf.text)
                    if inf.text not in Other_sections:
                        temp1 = getattr(x.find('text'), 'text', None)
                        if inf.text in ['ABSTRACT', 'CONCL']:
                            docs[numm].append(temp1 + " " + temp1)
                        else:
                            docs[numm].append(temp1)
        docs[numm] = list(filter(None, docs[numm]))
    res=docs.get(numm)
    # joining texts of each article into one string.
    # docs_list = [' '.join(res.get(doc)) for doc in res]
    a=" ".join(res)
    docs_list = []
    docs_list.append(a)
    xml_inpuit_list=[]
    xml_inpuit_list.append(numm)

    # joining texts of each article into one string.
    docs_list_all = [' '.join(docs.get(doc)) for doc in docs]
    #。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。 data_for_loc for the location。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。
    data_for_loc = [re.sub(r'\s', ' ', doc) for doc in docs_list]

    # Removing capital letters followed by digits like DM2, S2
    data_for_loc = [re.sub(r'[A-Z]+[0-9]+', '', doc) for doc in data_for_loc]

    # lower casing new line words:
    data_for_loc = [re.sub(r'\.\s[A-Z]{1}[a-z]{1,}\s', ' ', doc) for doc in data_for_loc]

    # removing numbers really helps avoiding wrong GPE entities:
    data_for_loc = [re.sub(r'\d+', '', doc) for doc in data_for_loc]

    # Replacing US, USA, EU, UK, and UAE with their complete names because we don't want them to be removed in the next step:
    data_for_loc = [re.sub(r'US', 'the United States', doc) for doc in data_for_loc]
    data_for_loc = [re.sub(r'USA', 'the United States', doc) for doc in data_for_loc]
    data_for_loc = [re.sub(r'EU', 'Europe', doc) for doc in data_for_loc]
    data_for_loc = [re.sub(r'U.S.', 'the United States', doc) for doc in data_for_loc]
    data_for_loc = [re.sub(r'UK', 'United Kingdom', doc) for doc in data_for_loc]
    data_for_loc = [re.sub(r'UAE', 'United Arab Emirates', doc) for doc in data_for_loc]

    # removing punctuations:
    punctuation = '!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'
    data_for_loc = [re.sub(r'[{}]+'.format(punctuation), '', doc) for doc in data_for_loc]

    # Removing words with all capital letters like 'VAERD','RVEF','DM':
    data_for_loc = [re.sub(r'[A-Z]{2,}', '', doc) for doc in data_for_loc]
    #。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。 data_for_loc for the location。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。



    ################################################################################################################################################################################################
    ################################################################################################################################################################################
    ################################################################################################################################################################################################
    #################################################################################################################################################################################################
    nlp = spacy.load("en_core_web_sm")
    # nlp = spacy.load("en_core_web_md")

    # nlp of articles data
    data1 = [nlp(doc) for doc in data_for_loc]

    entities = [[] for doc in data1]  # to contain entities
    labels = [[] for doc in data1]  # to contain entity lables
    # position_start=[[] for doc in data1 ]
    # position_end=[[] for doc in data1 ]


    for k, doc in enumerate(data1):
        for ent in doc.ents:
            # print(ent.text,ent.label_)
            if ent.text not in wrong_entities:
                entities[k].append(ent.text)
                labels[k].append(ent.label_)
                # print(entities[k])
            # position_start[k].append(ent.start_char)
            # position_end[k].append(ent.end_char)

    # Creating data frames of entities and labels of each article:
    df = [[] for doc in data1]
    df_fltd = [[] for doc in data1]  # we will filter data frames for taking only GPE labels
    GPE_top3 = dict.fromkeys(xml_inpuit_list)  # A dictionary of Top3 most frequent GPEs of each article

    for k, doc in enumerate(data1):
        df[k] = pd.DataFrame({'Entities': entities[k], 'Labels': labels[k]})

        # Filter the data frames to contain only GPE labels
        GPE_top3[xml_inpuit_list[k]] = df[k][df[k].Labels == 'GPE']['Entities'].value_counts().to_dict()
    for i, ppr in enumerate(GPE_top3):
        # plt.figure(figsize=(24, 22))  # width:20, height:3
        plt.bar(list(GPE_top3[ppr].keys()), list(GPE_top3[ppr].values()))
        plt.title(f'The location in the  {xml_inpuit_list[i]}')
        plt.xticks(rotation=45, fontsize=11)

        plt.savefig(f'Location_figure_{xml_inpuit_list[i]}', bbox_inches="tight")
        plt.close()
# =================================   Trigrams project 2 for loc  ======================================
# =================================   Trigrams project 2 for loc  ======================================
# =================================   Trigrams project 2 for loc  ======================================

# =================================   Trigrams project 3 for des  ======================================
# =================================   Trigrams project 3 for des  ======================================
# =================================   Trigrams project 3 for des  ======================================
def To_Generate_Disease(number):
    number
    myinput = str(number)
    url = baseurl + str(myinput) + addurl
    html = askURL(url)  # Save the obtained web page source code
    # 2.Parse data one by one
    soup = BeautifulSoup(html, "html.parser")
    soup = str(soup)
    collection = ET.XML(soup)
    numm = str("PMC" + myinput)
    section_types = {}
    docs = {}
    section_types[numm] = []
    docs[numm] = []
    for i, document in enumerate(collection):

        for x in document.findall("passage"):
            # print(x.findall('infon'))
            infon_list = x.findall('infon')

            # Removing footnote and table contents sections:
            if any(inf.text == 'footnote' for inf in infon_list) or any(inf.text == 'table' for inf in infon_list):
                document.remove(x)

        for x in document.findall("passage"):
            for inf in x.findall('infon'):
                if inf.attrib == {'key': 'section_type'}:
                    section_types[numm].append(inf.text)
                    if inf.text not in Other_sections:
                        temp1 = getattr(x.find('text'), 'text', None)
                        if inf.text in ['ABSTRACT', 'CONCL']:
                            docs[numm].append(temp1 + " " + temp1)
                        else:
                            docs[numm].append(temp1)
        docs[numm] = list(filter(None, docs[numm]))
    res = docs.get(numm)
    # joining texts of each article into one string.
    # docs_list = [' '.join(res.get(doc)) for doc in res]
    a = " ".join(res)
    docs_list = []
    docs_list.append(a)
    xml_inpuit_list = []
    xml_inpuit_list.append(numm)
    # 。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。 data_for_des for the disease。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。
    data_for_des = [re.sub(r'\s', ' ', doc) for doc in docs_list]
    # data_for_des = [re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', ' ', doc) for doc in data_for_des]
    data_for_des = [re.sub(r'[\s\(][^-a-zA-Z]+\-*[^-a-zA-Z]+', ' ', doc) for doc in data_for_des]
    # Adding 2019 to -nCoV:
    data_for_des = [re.sub(r'-nCoV', '2019-nCoV', doc) for doc in data_for_des]
    data_for_des = [re.sub(r'\s', ' ', doc) for doc in data_for_des]

    # 。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。 data_for_des for the disease。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。。

    def display_entities(model, document):
        """
        This function displays word entities

        Parameters:
             model(module): A pretrained model from spaCy(https://spacy.io/models) or ScispaCy(https://allenai.github.io/scispacy/)
             document(str): Document to be processed

        Returns: list of named/unnamed word entities and entity labels
         """
        nlp = model.load()
        doc = nlp(document)
        entity_and_label = [[X.text, X.label_] for X in doc.ents]
        return entity_and_label


    entities = [[] for doc in data_for_des]
    labels = [[] for doc in data_for_des]
    df = [pd.DataFrame() for doc in data_for_des]
    disease_top3 = dict.fromkeys(xml_inpuit_list)
    for k, doc in enumerate(data_for_des):
        nlp = en_ner_bc5cdr_md.load()
        doc = nlp(doc)
        result = [[X.text, X.label_] for X in doc.ents]
        # result = display_entities(en_ner_bc5cdr_md, doc)

        for ent, lbl in result:
            if ent not in wrong_entities:
                entities[k].append(ent)
                labels[k].append(lbl)
        in_ = pd.DataFrame(list(entities[k]), columns=['entities'])
        out = pd.DataFrame(list(labels[k]), columns=['Labs'])
        # df[k] = in_.hstack(out)
        df[k] = pd.concat([in_, out],axis=1)
        if 'DISEASE' not in labels[k]:
            print(f'No diseases has been mentioned in {xml_inpuit_list[k]}')
            disease_top3[xml_inpuit_list[k]] = {'No Disease mentions': 0}
        else:
            disease_top3[xml_inpuit_list[k]] = df[k][df[k].Labs == 'DISEASE']['entities'].value_counts()[:3].to_dict()

    for i, ppr in enumerate(disease_top3):
        # plt.figure(figsize=(24, 22))  # width:20, height:3
        plt.bar(list(disease_top3[ppr].keys()), list(disease_top3[ppr].values()))
        plt.title(f'Top 3 disease for {xml_inpuit_list[i]}')
        plt.xticks(rotation=45, fontsize=11)

        plt.savefig(f'Disease_figure_{xml_inpuit_list[i]}', bbox_inches="tight")
        plt.close()
        # print(xml_inpuit_list[i][:-4])

# =================================   Trigrams project 3 for des  ======================================
# =================================   Trigrams project 3 for des  ======================================
# =================================   Trigrams project 3 for des  ======================================

# for html.............................................................................forhtml#
# for html.............................................................................forhtml#
# for html.............................................................................forhtml#
# To_Generate_Disease(6988269)
# To_Generate_Location(6988269)
# To_Generate_Key_Word(6988269)