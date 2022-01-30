import pandas as pd
import spacy
from spacy.matcher import Matcher
from spacy.language import Language
from slugify import slugify


def process_input(input):
    predictions = nlp(input)
    
    if (len(predictions) == 0):
        print('Prediction: []')
        return None
        
    for prediction in predictions:
        print('Prediction : {0} -> {1}'.format(prediction['start'], prediction['finish']))

    return (prediction['start'], prediction['finish'])


def check_french_city(city):
    slug = slugify(city, lowercase=True, separator=' ')
    search = cities.loc[france_cities['slug'] == slug]
    return True if (len(search) > 0) else False


def extract_cities(span):
    city_matcher = Matcher(nlp.vocab)
    city_pattern = [[{'ENT_TYPE':'LOC'}]]
    city_matcher.add('CITY', city_pattern)

    cities = []
    for idx, (match_id, start, end) in enumerate(city_matcher(span)):
        if (check_french_city(span[start:end].text)):
            cities.append(span[start:end].text)

    return cities


def lemAdpLoc1Pattern():
    lem_adp_loc_start = []
    for lemma in START_ACTIONS:
        pattern = [{'LEMMA': lemma},{'POS':'ADP'},{'ENT_TYPE':'LOC'}]
        lem_adp_loc_start.append(pattern)

    lem_adp_loc_finish = []
    for lemma in FINISH_ACTIONS:
        pattern = [{'LEMMA': lemma},{'POS':'ADP'},{'ENT_TYPE':'LOC'}]
        lem_adp_loc_finish.append(pattern)

    return {
        "LEM_ADP_LOC_START": lem_adp_loc_start,
        "LEM_ADP_LOC_FINISH":  lem_adp_loc_finish
    }


def processLemAdpLoc1Pattern(matcher_index, span, pending):
    if (matcher_index == "LEM_ADP_LOC_START"):
        cities = extract_cities(span)
        if 'start' in pending: pending = {}
        pending['start'] = cities[0]

    if (matcher_index == "LEM_ADP_LOC_FINISH"):
        cities = extract_cities(span)
        if 'finish' in pending: pending = {}
        pending['finish'] = cities[0]

    return pending


def adpLoc1AdpLoc2Pattern():
    adp_loc_adp_loc_start = []
    for adp in DESTINATION_ADPS:
        pattern = [{'ENT_TYPE':'LOC'},{'LEMMA': adp, 'POS':'ADP'},{'ENT_TYPE':'LOC'}]
        adp_loc_adp_loc_start.append(pattern)
    
    adp_loc_adp_loc_finish = []
    for adp in START_ADPS:
        pattern = [{'ENT_TYPE':'LOC'},{'LEMMA': adp, 'POS':'ADP'},{'ENT_TYPE':'LOC'}]
        adp_loc_adp_loc_finish.append(pattern)

    return {
        "ADP_LOC_ADP_LOC_START": adp_loc_adp_loc_start,
        "ADP_LOC_ADP_LOC_FINISH": adp_loc_adp_loc_finish
    }


def processAdpLoc1AdpLoc2Pattern(matcher_index, span, pending):
    if (matcher_index == "ADP_LOC_ADP_LOC_START"):
        cities = extract_cities(span)

        if len(cities) == 2:
            pending['start'] = cities[0]
            pending['finish'] = cities[1]

    if (matcher_index == "ADP_LOC_ADP_LOC_FINISH"):
        cities = extract_cities(span)

        if len(cities) == 2:
            pending['start'] = cities[1]
            pending['finish'] = cities[0]

    return pending


def loc1Loc2Pattern():
    return {
        "LOC_LOC": [[{'ENT_TYPE':'LOC'},{'ORTH': '-', 'OP': '?'},{'ENT_TYPE':'LOC'}]]
    }


def processLoc1Loc2Pattern(matcher_index, span, pending):
    if (matcher_index == "LOC_LOC"):
        cities = extract_cities(span)

        if len(cities) == 2:
            pending['start'] = cities[0]
            pending['finish'] = cities[1]

    return pending


def specificPattern():
    return {
        "SPECIFIC_START": [
            [{'LEMMA': 'départ'},{'ENT_TYPE':'LOC'}],
            [{'LEMMA': 'début'},{'ENT_TYPE':'LOC'}]
        ],
        "SPECIFIC_FINISH": [
            [{'LEMMA': 'arrivée'},{'ENT_TYPE':'LOC'}],
            [{'LEMMA': 'fin'},{'ENT_TYPE':'LOC'}],
        ],
    }


def processSpecificPattern(matcher_index, span, pending):
    if (matcher_index == "SPECIFIC_START"):
        cities = extract_cities(span)
        if 'start' in pending: pending = {}
        pending['start'] = cities[0]

    if (matcher_index == "SPECIFIC_FINISH"):
        cities = extract_cities(span)
        if 'finish' in pending: pending = {}
        pending['finish'] = cities[0]

    return pending


@Language.component("extract_targets")
def extract_targets(doc):
    matcher = Matcher(nlp.vocab)
    for pattern in patterns:
        matcher.add(pattern, patterns[pattern])

    targets = []
    pending = {}

    for match_id, start, end in matcher(doc):
        matcher_index = doc.vocab.strings[match_id]

        for processor in processors:
            pending = processor(matcher_index, doc[start:end], pending)

        if (len(pending) == 2):
            targets.append(pending)
            pending = {}

    return targets


PATH_CITY = 'dataset/cities.csv'
START_ACTIONS = ['partir','être','venir','train','trajet']
FINISH_ACTIONS = ['rendre','aller','arriver']
START_ADPS = ['de','depuis']
DESTINATION_ADPS = ['a','à','au','aux','en','vers']

# Load french cities for checking
france_cities = pd.read_csv(PATH_CITY)
cities = france_cities.loc[france_cities['department_code'].str.contains("^\d\d$", case=False)]

# Loads patterns
patterns = {}
patterns.update(lemAdpLoc1Pattern())
patterns.update(adpLoc1AdpLoc2Pattern())
patterns.update(loc1Loc2Pattern())
patterns.update(specificPattern())

# Loads process patterns
processors = [
    processLemAdpLoc1Pattern,
    processAdpLoc1AdpLoc2Pattern,
    processLoc1Loc2Pattern,
    processSpecificPattern
]

# Init NLP Service
nlp = spacy.load('fr_core_news_lg')
nlp.add_pipe('extract_targets')