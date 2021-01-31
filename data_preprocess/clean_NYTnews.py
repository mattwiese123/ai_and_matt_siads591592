import pickle
import pandas as pd


if __name__ == '__main__':
	results = pickle.load(open('../data_collect/NYTnews2020.pkl', 'rb'))
	NYTnews_keyword_count = []

	# iterate through 12 months' data
	for x in range(12):    
	    json_data = results[x]
	    length = len(json_data['response']['docs'])

	    corona = 0
	    # define covid related keywords 
	    word_list = ['corona', 'covid', 'virus', 'vaccine', 'pandemic', 'social distancing']

	    unrelated_abs = []
	    for i in range(length):    
	        try:
	            abstract = (json_data['response']['docs'][i]['abstract'].lower())
	            essay_type = json_data['response']['docs'][i]['subsection_name']
	            if any([x in abstract for x in word_list]):
	                corona+=1
	                #print(essay_type, '**', abstract)
	            else:
	                unrelated_abs.append(abstract)
	        except:
	            continue

	    NYTnews_keyword_count.append([x+1, corona, round(corona/length*100,3)])

	news_count = pd.DataFrame(NYTnews_keyword_count)
	news_count.columns = ['month', 'covid_kw_count', 'mention_per_news']
	news_count.to_csv('../plotly/NYTnews_keyword_monthly.csv')
