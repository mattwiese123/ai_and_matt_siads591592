import requests
import pickle
import time


if __name__ == '__main__':
	nyt_key = 'o1BpGCWsjVAaily2pf7cwKoG5AljUuC6'
    results = []

	for month in range(1,13):
	    print(month)
	    month = str(month)
	    nyt_api = f'https://api.nytimes.com/svc/archive/v1/2020/{month}.json?api-key={nyt_key}'
	    r = requests.get(nyt_api)
	    json_data = r.json()
	    results.append(json_data)
	    time.sleep(20)
	    
	pickle.dump(results, open('NYTnews2020.pkl', 'wb'))