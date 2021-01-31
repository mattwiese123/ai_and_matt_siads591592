import pandas as pd

def is_in_sentence(x):
	"""
	check if the first sentence is a brief description
	"""
    sentences = x.split('\n')
    for ind, sent in enumerate(sentences):
        if ' is ' in sent or 'business' in sent or 'based in' in sent:
            target = sent
            if target.endswith(' '):
                target+=sentences[ind+1]
            return target
    return 'None'


def replace_brackets(x):
	"""
	remove the citation marks from wikipedia
	"""
    import re
    return re.sub(r'\[\d+\]', '', x)



if __name__ == '__main__':
	comps = pd.read_csv('../plotly/sp500.csv', index_col=0)
	comps['comp_description'] = comps['comp_description'].str.strip()

	comps['comp_description2'] = comps['comp_description'].apply(is_in_sentence)
	comps['comp_description2'] = comps['comp_description2'].apply(replace_brackets)
	# for checking some irregularities:
	comps['len2'] = comps['comp_description2'].apply(len)

	comps.to_csv('../plotly/sp500_comp_description.csv')