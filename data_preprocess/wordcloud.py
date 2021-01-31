import pandas as pd
from wordcloud import WordCloud, STOPWORDS
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from string import punctuation
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import pickle
import numpy as np
from collections import Counter


def clean_text(docs):
    # docs: a list of documents that need to be analyzed
    lemmatizer = WordNetLemmatizer()
    lemm_docs = []

    for doc in docs:
        words = word_tokenize(doc)
        lemm_docs.append(' '.join([lemmatizer.lemmatize(x) for x in words
                                   if x not in punctuation and not x.isdigit()]))
    return lemm_docs



if __name__ == '__main__':
	news = pickle.load(open('../data_collect/NYTnews2020.pkl', 'rb'))
	monthly=[]
	for x in range(12):    
	    json_data = news[x]
	    length = len(json_data['response']['docs'])
	    
	    this_month=''
	    types=[]
	    for i in range(length):    
	        abstract = json_data['response']['docs'][i]['abstract'].lower()
	        try:
	            essay_type = json_data['response']['docs'][i]['subsection_name']
	        except:
	            essay_type = 'NO TYPE'
	        this_month+=abstract+'; '
	        types.append(essay_type)
	        
	    monthly.append(this_month)

	cleaned_monthly = clean_text(monthly) 
	stopwords = list(STOPWORDS)+['see','look','nytimes', 'today']
	tfidf_vectorizer = TfidfVectorizer(max_features=20000,  # only top 5k by freq
	                                   lowercase=True,  # drop capitalization
	                                   ngram_range=(1, 2),
	                                   min_df=2,  # note: absolute count of doc
	                                   max_df=0.95,  # note: % of docs
	                                   token_pattern=r'\b[a-z]{3,12}\b',  # remove short, non-word-like terms
	                                   stop_words=stopwords)  # default English stopwords
	tfidf_documents = tfidf_vectorizer.fit_transform(cleaned_monthly)
	tfidf_documents_array = tfidf_documents.toarray()
	feature_names = tfidf_vectorizer.get_feature_names()

	results = []
	words_to_remove = []

	for counter, doc in enumerate(tfidf_documents_array):
	    tf_idf_tuples = list(zip(feature_names, doc))
	    one_doc_as_df = pd.DataFrame.from_records(tf_idf_tuples,
	                                              columns=['term', 'score']).sort_values(by='score',
	                                                                                     ascending=False).reset_index(
	        drop=True)
	    # get the first 100 important words
	    results.append(one_doc_as_df.iloc[:100])
	    # save all the rest just in case
	    words_to_remove += (one_doc_as_df.iloc[100:]['term'].tolist())


	wordcloud = WordCloud(width=800, height=800, background_color='white',
                      stopwords=stopwords, margin=4, font_step=1)

	for i in range(len(results)):
	    term_freq_dict = results[i].set_index('term').T.to_dict('record')[0]
	    if 0 in term_freq_dict.values():
	        term_freq_dict = dict([(k, v) for k, v in term_freq_dict.items() if v != 0])
	    wordcloud.generate_from_frequencies(term_freq_dict)
	    plt.figure(figsize=(8, 8), facecolor=None)
	    plt.imshow(wordcloud)
	    plt.axis("off")
	    plt.tight_layout(pad=0)
	    plt.title(f'NYT_News_2020_M{i+1}')
	    plt.savefig(f'../wordclouds/NYT_News_2020_M{i+1}'+'.jpg')
	    plt.close()


