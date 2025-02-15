# AI-Summit-Hackathon

## Sujet  

Le sujet ci-dessous est une proposition. Il est tout à fait possible de changer si :  
- nous avons une meilleure idée  
- si l'orga du hackathon nous indique que notre sujet n'est pas suffisamment proche de Doctolib et de la santé en France et que par conséquent il faut l'adapter ou le changer  

## Problématique  

Les invasions de sauterelles en Afrique, Asie, Amérique et Australie représentent un enjeu de santé majeur, détruisant des cultures, et très difficilement prévisible. Le but serait alors de prévoir les déplacements des essaims, qui peuvent aller jusqu'à 140 km par jour.  

Une meilleure prévision des essaims permet alors de traiter les cultures. Ce traitement est aujourd'hui majoritairement chimique car l'effet de tels produits est plus rapide que les biopesticides qui existent actuellement. Une meilleure prévision permet alors :  
1. d'utiliser des biopesticides, ce qui permet  
   - d'éviter les pénuries de bouffe  
   - d'éviter de niquer la santé des gens qui mangent ces produits remplis de pesticides nocifs  

## Approche  

L'idée serait de s'appuyer sur la carte des recensements des invasions de sauterelles et criquets et la combiner à des cartes d'informations des sols.  

Seul problème : c'est de la data tabulaire donc un XGBoost ou un truc du genre sera sûrement le plus performant et on aurait bien aimé profiter de l'occasion et des ressources mises à disposition pour faire du deep. Comment faire ?

Sinon, l'article 5 parle du fait que c'est important de prédire la où les essaims peuvent se déplacer, mais aussi de les track en direct pour mieux prédire la ou ils vont aller. Et savoir ou ils sont se fait par image satellite. Par contre, par sur qu'on ai un dataset avec une GT pour ca ...

## Ressources  

### Articles et papiers
- [Article](https://globalhealth.euclid.int/fr/the-public-health-implication-of-the-2020-locust-invasion-in-east-africa/)
- [Site plutot officiel](https://www.fao.org/interactive/desert-locusts/en/)
- [Paper 1 qui etudie les invasions en australie](https://www.nature.com/articles/s41598-020-73897-1)
- [Article qui parle d'une solution pour track les essaims par radar](https://www.nature.com/articles/s41598-024-81553-1)
- [Ressource intéressante](https://gda.esa.int/story/desert-locust-monitoring-in-east-africa/)
- [liens en bas de l'article](https://earthobservatory.nasa.gov/images/148314/soil-data-aids-prediction-of-locust-swarms)


### Datasets  
- [Dataset d'info des sols](https://www.isric.org/explore)
- [On a fait la demande de ce dataset privé](https://locust-hub-hqfao.hub.arcgis.com/)
- [Dataset Kaggle](https://www.kaggle.com/datasets/souravsamrat/locust-watch-dataset-across-globe)


