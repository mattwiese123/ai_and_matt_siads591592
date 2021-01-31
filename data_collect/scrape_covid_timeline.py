import requests
import pickle
import time
from bs4 import BeautifulSoup


if __name__ == '__main__':
	link = 'https://www.ajmc.com/view/a-timeline-of-covid19-developments-in-2020'
	raw = requests.get(link)
	soup = BeautifulSoup(raw.content, 'lxml')

	timeline = [x.text for x in soup.find_all('strong')]
	timeline = [x.split(' — ') for x in timeline]
	timeline_df = pd.DataFrame(timeline)
	timeline_df.columns = ['date', 'content']
	timeline_df['date'] = pd.to_datetime('2020 '+timeline_df['date'])

	timeline_df.to_csv('../plotly/COVID_timeline.csv')
