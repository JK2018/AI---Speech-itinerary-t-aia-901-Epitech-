import numpy as np
import pandas as pd
import string
import re
import pymongo
import langdetect
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import FrenchStemmer
from nltk import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.stem import RegexpStemmer
import spacy
from spacy.lang.fr.examples import sentences 
from spacy import displacy

nlp2 = spacy.load("fr_core_news_sm")

client = pymongo.MongoClient("mongodb+srv://admin:admin@clusteria.tvj6u.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client['iadb']
collection = db['spamfilterParams']


# p_word_given_ham = collection.find_one({'_id': "p_word_given_ham" })['data']
# p_word_given_spam = collection.find_one({'_id': "p_word_given_spam" })['data']
parameters_spam = collection.find_one({'_id': "parameters_spam" })['data']
parameters_ham = collection.find_one({'_id': "parameters_ham" })['data']
p_ham = collection.find_one({'_id': "p_ham" })['data']
p_spam = collection.find_one({'_id': "p_spam" })['data']


collection = db['cities']
cursor = collection.find({})
fields = ['stop_name']
cityList = pd.DataFrame(list(cursor), columns = fields)


def process_spam_filter(message):

    """
    IN : model params, user input
    OUT : model s prediction (ham / spam)
    USE : func that predicts weather a user input is spam or ham by
          applying our model params to a Naive Bayes model
          also checks for FR lang, and number of cities in the input
          Used for predicting user input.
    """

    def detect_lang(text):
        """
        IN: string
        OUT: string
        USE: returns the lang code (ex: 'fr') from the best predicted language
        """
        result = langdetect.detect_langs(text)
        lang = str(result[0])[:2]
        return lang


    def check_two_cities(message, cityList):
        """
        IN: string, list of cities extracted from our stop_names
        OUT: int
        USE: returns number of cities from the string that correspond to a stop_name
        """
        doc = nlp2(message) #lower

        def saveAllCitiesInArray():
            cities = []
            for city in doc.ents:
                cities.append(city.text)
            return cities
        cityArr = saveAllCitiesInArray()

        def checkCity(city):
            # city = city.lower()
            city = city.replace("-", " ")
            city = city.replace("saint", "st")
            result = 0
            for index, row in cityList.iterrows():
                processedStopName = row['stop_name'].replace("-", " ").lower()
                if (city in processedStopName):
                    result = 1
                    break
                else:
                    result = 0
            return result


        nbCitiesConfirmed = 0
        for c in cityArr:
            nbCitiesConfirmed = nbCitiesConfirmed + checkCity(c)

        return (nbCitiesConfirmed)


    def preprocess_string(string):
        """
        IN : user input
        OUT : cleaned user input
        USE : will set all to lowercase, remove punctuation and stopwords,
              remove trailing and double spaces
        """
        # set all to lowercase
        # string = string.lower()
        # remove punct
        string = string.replace('[^\w\s]',' ')
        # remove stop words
        stop = stopwords.words('french')
        string = ' '.join([word for word in string.split(" ") if word not in stopwords.words('french')])
        # replace double space by single space
        string = string.replace('  ',' ')
        # strip spaces
        string = string.strip()
        return string

    result = ""
    # check cities
    nb_of_cities = check_two_cities(message, cityList)

    # check lang
    lang = detect_lang(message)

    message = message.replace(',','')
    message = message.replace('-','')
    message = message.replace(' -','')
    message = message.replace(' /','')
    message = re.sub('\W', ' ', message)
    message = preprocess_string(message)

    message2 = ""
    doc = nlp2(message)
    for token in doc:
        message2 = message2+ " "+token.lemma_

    if lang != 'fr' and len(doc) > 3:
        result = 'spam'
    else:
        if nb_of_cities < 2:
            result = 'spam'
        else:

            message2 = message2.lower().split()
            p_spam_given_message = p_spam
            p_ham_given_message = p_ham

            for word in message2:
                if word in parameters_spam:
                    p_spam_given_message *= parameters_spam[word]

                if word in parameters_ham: 
                    p_ham_given_message *= parameters_ham[word]

            if p_ham_given_message > p_spam_given_message:
                result = 'ham'
            elif p_ham_given_message < p_spam_given_message:
                result = 'spam'
            else:
                result = 'ham'
               #result = 'Equal proabilities, have a human classify this!'

    return result == 'spam'


def checkOtherRequest(message):
    sleepList = ['chambre','hotel','hôtel','nuit','lit','lits','nuits','chambres']
    eatList = ['manger', 'table', 'restaurant', 'dinner', 'repas', 'boire', 'verre']
    showList = ['spectacle', 'musée', 'théatre', 'concert', 'ciné', 'cinéma', 'film']
    transportList = ['avion', 'vol', 'bateau', 'croisière','bus','autobus','autocar','automobile']

    if( any(substring in message for substring in sleepList) ):
        return "Nous ne pouvons donner suite à votre demande, veuillez vous orienter vers Booking.com ou Expedia.com."

    elif( any(substring in message for substring in eatList) ):
        return "Nous ne pouvons donner suite à votre demande, veuillez vous orienter vers Lafourchette.com."

    elif( any(substring in message for substring in showList) ):
        return "Nous ne pouvons donner suite à votre demande, veuillez vous orienter vers BilletReduc.com ou TicketMaster.com."

    elif( any(substring in message for substring in transportList) ):
        return "A notre grand regret, nous ne proposons pas d'itinéraires pour ce mode de transport."

    else:
        return "Nous ne pouvons malheureusement pas traiter votre demande. Si vous souhaitez connaitre un itinéraire, merci de bien vouloir essayer à nouveau en reformulant votre demande."