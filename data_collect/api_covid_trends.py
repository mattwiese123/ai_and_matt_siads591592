from serpwow.google_search_results import GoogleSearchResults
import json
import pickle


if __name__ == "__main__":

	# create the serpwow object, passing in our API key
	ai_api = "request_online"
	serpwow = GoogleSearchResults(ai_api)

	# set up a dict for the search parameters
	params = {
	    "q" : "covid",
	    "search_type": "trends"

	}

	# retrieve the search results as JSON
	result = serpwow.get_json(params)
	pickle.dump(result, open('covid_trends.pkl', 'wb'))