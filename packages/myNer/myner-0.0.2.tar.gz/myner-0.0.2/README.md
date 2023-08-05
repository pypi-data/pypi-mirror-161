
# NER-API
Ce package permet le traitemnt du texte , l'extraction des entités(inclus code swift et code imo), ainsi que le highlighting des ces entités présente dans un fichier pdf




## Installation 
```batch
pip install myNer
```


## Usage/Exemples
### Preprocessing:

```python
import myNer  
myNer.text_preprocessing.text_preprocessing(text,accented=True,stopw=True,punctuation=True,lowercase=True,lemmatize=True,spelling=True,expand_contraction=True,urls=True)
```
cette fonction permet de traiter le text en utilisant les filtres présents comme argument
```python
import myNer  
myNer.text_preprocessing.spacy_preprocessing(text,lowercase=True,stopw=True,punctuation=True,alphabetic=True,lemmatize=True,)
```
Permet de faire du traitement du texte à l'aide de spacy 


Après le preprocessing tout les caractères sont en miniscule, les retour en ligne et les multiples espaces sont éliminés , seulement un seul espace est ajouté lorsqu'on reconstitue le texte, les caractères spéciaux sont supprimés ,meme les "-" et les "+" sont supprimés dans les codes et les references ce qui peut poser problème, toutefois les fonctions du preprocessing possèdent des filtres qu'on peut ajuster selon le cas
### Méthodes d'extraction des entités:
on a utilisé dans ce projet :

1)reconnaissance à l'aide d'expression régulière:
```python
ner.find_imo(text)
ner.find_swift(text)
```
2) reconnaissance à l'aide de composante ner du modèle linguistique de spacy:
```python
ner.ner_spacy(text)
```
3) reconnaissance à l'aide des dictionnaires et du fuzzy matching:
```python
ner.ner_dicts(text,db,table)
```
Après avoir créer une base de données postgresql pour les ports , banques et navires , on utilise cette db pour extraire les entités de ce type.
Sauf que cette méthode se montre dépendante des données présentes dans la base de données(par exemple si le nom compet d'une banque est présent dans la base, un nom courant de la banque ne sera pas reconnu )



### Pdf highlighting:

```python
import myNer  
myNer.highlight_pdf.output(input_file)

```
cette fonction prend en argument le chemin vers un fichier pdf , extrait les entités,les highlight , et enregistre le pdf highlighté dans le dossier courant sous le nom "output.pdf"

Il existe aussi deux fonctions pour l'encodage du pdf en base64 et l'inverse,pour permettre l'interaction avec l'API
```python
highlight_pdf.pdf_to_base64(pdf)
highlight_pdf.base64_to_pdf(base64)
```



## API Reference

#### get_entities(text)
Prend un texte(String) et retourne ses entités
#### highlight_pdf(pdf)
Prend le pdf encodé en base64 et retourne le pdf highlighté encodé en base64 ainsi que les entités détectées sous format :    # positions format: a dict containing entities as keys, and the values a list of tuples:(list of Rect positions,page number)
    