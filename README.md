# T-IAI-901-MSC2022 - GROUP 18

## Gestion de projet
Notre travail a été organisé et réparti dans un Trello.

https://trello.com/b/X3s2fpPJ/ia-projet

## Installer les dépendances du projet

### Dépendances obligatoires pour les Jupyter Notebook

```bash
pip install notebook
pip install numpy
pip install pandas
pip install matplotlib
pip install scikit-learn
pip install pymongo
pip install langdetect
pip install nltk
pip install dnspython
pip install python-slugify
pip install spacy
python -m spacy download fr_core_news_sm
python -m spacy download fr_core_news_lg

# Reconnaissance vocale
sudo apt-get install portaudio19-dev
pip install PyAudio
pip install SpeechRecognition
```

### Dépendances supplémentaires obligatoires pour l'interface web
```bash
pip install Flask
pip install python-dotenv
pip install simplejson
```

## Interface web

### Installer la plateforme
- Créer un projet sur Google Maps Platform.
- Activer les APIs **Directions API** et **Maps JavScript API**.
- Créer une clé API depuis la Google Maps Platform pour utiliser les services.
- Copier le contenu du fichier `app/.flasken.example` dans un nouveau fichier `app/.flaskenv`
- Ajouter la clé API dans la variable `GOOGLE_API_KEY`

### Lancer la plateforme
- Se rendre dans le dossier `/app`.
- Lancer la commande `flask run`.
- La plateforme est accessible à l'adresse http://localhost:8000/

## Notes
L'ensemble du projet a été développé avec les versions suivantes. Des versions différentes peuvent altérer les performances des algorithmes.

```
Python - version 3.10.0
Spacy - version 3.1.3
fr-core-news-sm - version 3.1.0
fr-core-news-lg - version 3.1.0
```

