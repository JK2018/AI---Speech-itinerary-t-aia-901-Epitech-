import spacy
from spacy.lang.fr.examples import sentences 
from spacy import displacy
nlp = spacy.load("fr_core_news_sm")



countries = [] # countries
verbs = [] # verbs
verbs_lemma = [] # verbs
new_dict = {} # dico used to stock index of each word in phrase
verbs_initial_depart = ['aimer','quitter', 'partir', 'retour', 'prendre'] # utiliser l'infinitif facilite lemantization
verbs_initial_arriver = ['arriver', 'rendre', 'effectuer', 'aller'] 

# Process whole documents
# De preference, il faudrait avoir deux verbes dans la phrase
# Je voudrais arriver à Paris en partant de Caen. # phrase init

text = ("Paris en venant de Marseille")
#text = resulat #receive stt resultat
doc = nlp(text) #lower

#declaration des vars
#indexDepart = 0 #Index du verbe de depart
#indexArriver = 0 #Index du verbe d'arriver

# stocker tous les elements de la phrases dans une dico avec leur index
def wordsTokenisation():
    for sent in doc.sents:
        for token in sent:
            #print(token.i - sent.start, token.text)
            new_dict[token.i - sent.start] = token.text
    print("dico_words : ",new_dict)

# stocker tous les verbs dans une liste
def saveVerbsInArray():
    for item in doc:
        #print(item.text, item.pos_)
        if(item.pos_ == "VERB" and (item.lemma_ in verbs_initial_depart or item.lemma_ in verbs_initial_arriver)):
            verbs.append(item.text)
            verbs_lemma.append(item.lemma_)
    print("users_verbs : ",verbs)
    print("users_verbs_lemma : ",verbs_lemma)
    
# stocker tous les noms de villes dans une liste
def saveAllCitiesInArray():
    for city in doc.ents:
        countries.append(city.text)
    print("countries : ",countries)
    
    
def foundWordIndexDico(itemText):
    for index, word,  in new_dict.items(): 
        #print(index, " - ",word)
        if itemText == word:
            return index
        
def foundCountryIndexDico(country):
    key_list = list(new_dict.keys())
    val_list = list(new_dict.values())
    position = val_list.index(country)
    #print("index : ",key_list[position])
    return key_list[position];     

# comparer une Lemmatization des verbes avec ceux ecrits dans verbs_depart
def detectIndexOfeachVerbs():
    indexDepart = 0
    indexArriver = 0
    for item in doc:
        if(item.pos_ == "VERB"):
            if(item.lemma_ in verbs_initial_depart and (item.lemma_ in verbs_initial_depart or item.lemma_ in verbs_initial_arriver)):
                indexDepart = foundWordIndexDico(item.text)
                print("verbs de depart : ",item.text," -> ",item.lemma_, " -> ",indexDepart)
            if(item.lemma_ in verbs_initial_arriver and (item.lemma_ in verbs_initial_depart or item.lemma_ in verbs_initial_arriver)):
                indexArriver = foundWordIndexDico(item.text)
                print("verbs d'arriver : ",item.text," -> ",item.lemma_, " -> ",indexArriver)
    return (indexDepart,indexArriver)

def foundDepartureCountry(indexDepart,indexArriver):
    departure = ""
    arrival = ""
    verbDepart = ""
    verbArrival = ""
    V1C1 = ""
    V1C2 = ""
    V2C1 = ""
    V2C2 = ""
    
    if(len(verbs) != 0):
        V1C1 = abs(foundCountryIndexDico(countries[0]) - indexDepart) #distance entre le Verbe1 et Ville1
        V1C2 = abs(foundCountryIndexDico(countries[1]) - indexDepart) #distance entre le Verbe1 et Ville2
        V2C1 = abs(foundCountryIndexDico(countries[0]) - indexArriver) #distance entre le Verbe2 et Ville1
        V2C2 = abs(foundCountryIndexDico(countries[1]) - indexArriver) #distance entre le Verbe2 et Ville2
    
    if(len(verbs) == 0):
        departure = countries[0]
        arrival = countries[1]
        
    elif (len(verbs) == 1):
        print("verb_0 : ",verbs[0])
        if(verbs_lemma[0].lower() in verbs_initial_depart):
            print("_verbs_initial_depart_ ")
            if V1C1 < V1C2 :
                departure = countries[0]
                arrival = countries[1]
            else:
                departure = countries[1]
                arrival = countries[0]
        else:
            print("_verbs_initial_arrival_")
            if V1C1 < V1C2 :
                arrival = countries[0]
                departure = countries[1]
            else:
                arrival = countries[1]
                departure = countries[0]
                
    elif (len(verbs) == 2):
        res1 = V1C1 + V2C2
        res2 = V1C2 + V2C1
        print("res1 : ",res1," res2",res2)
        res = min(res1,res2)
        print("min : ",res)
        if(res1 == res2):
            print("-1-",indexDepart , indexArriver)
            if(indexDepart < indexArriver):
                print("-1-1")
                if(foundCountryIndexDico(countries[0]) < foundCountryIndexDico(countries[1])):
                    print("-1-1-2")
                    departure = countries[0]
                    arrival = countries[1]
                else:
                    print("-1-1-3")
                    departure = countries[1]
                    arrival = countries[0]
                    
            elif(indexArriver < indexDepart):
                print("-1-2")
                if(foundCountryIndexDico(countries[0]) < foundCountryIndexDico(countries[1])):
                    print("-1-2-1")
                    departure = countries[1]
                    arrival = countries[0]
                else:
                    print("-1-2-2")
                    departure = countries[0]
                    arrival = countries[1]
                
            
        else:
            if res == res1:
                departure = countries[0]
                arrival = countries[1]
            elif res == res2:
                departure = countries[1]
                arrival = countries[0]
            
        
        
                
    print("V1C1 : ",V1C1,"-> V2C2 : ",V2C2, "V1C2 : ",V1C2,"-> V2C1 : ",V2C1,)      
    print("Départ : ",departure,"-> Arriver : ",arrival)
    return (departure,arrival)
 
def display():
    displacy.render(doc, style='dep', jupyter=True, options={'distance': 80})
    displacy.render(doc, style='ent', jupyter=True, options={'distance': 80})
    

def main():
    display()
    wordsTokenisation()
    saveVerbsInArray()
    saveAllCitiesInArray()
    indexVerb1,indexVerb2 = detectIndexOfeachVerbs()[0],detectIndexOfeachVerbs()[1]
    foundDepartureCountry(indexVerb1,indexVerb2)
    

main()

