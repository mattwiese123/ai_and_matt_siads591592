import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
	l='https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
	raw = requests.get(l)
	soup = BeautifulSoup(raw.content, 'lxml')

	table = soup.find_all('table')[0]
	results = [[y.text.strip() for y in x.find_all('td')] for x in table.find_all('tr')]
	titles = [x.text.strip() for x in table.find('tr').find_all('th')]
	sp500 = pd.DataFrame(results[1:])
	sp500.columns = titles
	# sp500.to_csv('sp500.csv')

	# ==== scrape company description page in wikipedia ======
	link_df = pd.DataFrame([[y.find('a') for y in x.find_all('td')] for x in table.find_all('tr')][1:])
	link_df[0] = link_df[0].apply(lambda x: x['href'])
	link_df[1] = link_df[1].apply(lambda x: x['href'])
	link_df[2] = link_df[2].apply(lambda x: x['href'])
	link_df.columns = ['nyse', 'wiki_comp', 'sec', 'x','x','x','x','x','x']
	link_df = link_df.drop('x',1)
	link_df['wiki_comp'] = 'https://en.wikipedia.org'+ link_df['wiki_comp'] 
	sp500 = pd.concat([sp500, link_df], axis=1)
	sp500 = sp500.rename(columns={'Security':'Company_Name'})
	sp500 = sp500.drop('SEC filings',1)
	wiki_comp_links = sp500['wiki_comp'].tolist()

	comp_desc = []
	for l in wiki_comp_links:    
	    raw = requests.get(l)
	    soup = BeautifulSoup(raw.content, 'lxml')
	    content = ''.join([x.text for x in soup.find_all('p')])
	    comp_desc.append(content)
	    
	sp500['comp_description'] = comp_desc
	sp500.to_csv('../plotly/sp500.csv')