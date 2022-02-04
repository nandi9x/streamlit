Comment installer le programme sur votre ordinateur?

1 - Aller dans le repository du projet original https://github.com/nandi9x/streamlit 
2 - Cliquer sur l'icône "code" en vert 
3 - Il faut cloner le repository sur votre ordinateur, soit en téléchargant le dossier ZIP, soit en utilisant la commande git clone 'link'
4 - Une fois installé dans l'ordinateur, le mieux est de mettre les fichiers à extraire dans le même dossier mais facultatif
5 - Installer tous les frameworks en tapant la commande pip install -r /path/to/requirements.txt (mettre votre propre path, pour le trouver sous windows : https://fr.wikihow.com/trouver-le-chemin-pour-un-fichier-sous-Windows)

Vous pouvez maintenant lancer le programme en allant sur le terminal et en tapant:
streamlit run path/paie_streamlit.py (clique droit sur paie_streamlit > propriétés > copier collier l'emplacement OU alors glisser le fichier directement sur le terminal)
exemple : streamlit run C:\Users\ypyea\Documents\Nanda\EFREI\stage M1\Github\streamlit\paie_streamlit.py 
Un lien local s'affichera, ouvrez-le sur un navigateur web 

Concernant l'interface web :
- Le nom du csv ou json sera toujours paie.csv/json. Si vous voulez le renommer, il faut aller directement dans le code source.
- pour l'option ajout de multiples files, ne faire cette étape quand un seul coup. Si vous voulez ajouter d'autres documents, aller dans single files. Vous pouvez par la suite retournez dans multiples files
- Très important de rentrer le path des fichiers à extraire (aller sur lien de l'étape 5 si vous ne savez pas où le trouver). Si les fichiers à extraire sont dans le même dossier que le fichier python, pas besoin de path
- Vous pouvez rentrer 2 mêmes fichiers dans le csv, donc faites attention (sécurité à développer par la suite) 
- Si vous supprimez le csv, tout sera remis à 0 et l'extraction se fera à partir du premier fichier à extraire après supression 

Pour plus de questions, contactez:
ananda.yeann@efrei.net 
