import os
from pdfminer.high_level import extract_text
import streamlit as st 
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import re 
from io import StringIO
import pandas as pd 
import csv
from csv import DictWriter
import json 
from pathlib import Path
import os.path
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import MWETokenizer


st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_title="ETIXWAY",
    page_icon=None, 
)


def count(df):
    index = df.index
    number_of_rows = len(index)
    return(number_of_rows)


###########----FORMAT 1 RH----############

#------------ PRENDRE CONTENU PDF ------------#
def get_pdf_file_content(path):
    
    resource_manager = PDFResourceManager(caching=True)
    out_text = StringIO()
    codec = 'utf-8'
    laParams = LAParams()
    text_converter = TextConverter(resource_manager, out_text, laparams=laParams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(resource_manager, text_converter)
    for page in PDFPage.get_pages(fp, pagenos=set(), maxpages=0, password="", caching=True, check_extractable=True):
        interpreter.process_page(page)
    text = out_text.getvalue()
    
    fp.close()
    text_converter.close()
    out_text.close()

    return text

#------------ EXTRACTION ------------#
def create_extract_file(input_text): #créer un fichier file et extrait les données
    
    #Ouverture fichier et mise en forme liste 
    f = StringIO(input_text)

    mylist = [line.rstrip('\n') for line in f]
    while '' in mylist:      
        mylist.remove('')
    

    
     
    #Extraction mots 
    date_index = mylist.index("Paye du : ")
    a= (mylist[date_index+1])
    b=  str(a).strip('[]') #list to str pour prendre substring
    mois=(b[3:5])
 
    i = mylist.index("FONTENAY-SOUS-BOIS ")
    nom = (mylist[i+3])
    index_nom = mylist.index(nom) #chercher l'index du nom 
    
    adresse_index = mylist.index('Total brut   ')
    adresse = (mylist[index_nom+1:adresse_index]) #va donner plusieurs items d'une liste
    adresse = " ".join(adresse) #pour affichage meilleur 
    
    net_index = mylist.index('NET PAYE EN EUROS ')
    net= mylist[net_index+2]

    total_index= mylist.index('CONGES ')
    total = (mylist[total_index-1])

#------------ CREATION CSV ------------#

    new = {'Mois': mois, 'Nom': nom, 'Adresse': adresse,'Net_paye':net, 'Total_verse':total}
    field_names = ['Mois','Nom','Adresse','Net_paye','Total_verse']

    with open('paie.csv', 'a+', newline ='') as f_object:
        csv_writer = DictWriter(f_object,fieldnames=field_names )
        if f_object.tell() == 0:
                csv_writer.writeheader()
        news = csv_writer.writerow(new)
    
        f_object.close()
    
    f.close()
   
   
    
        
#------------ CREATION JSON ------------#

def csv_to_json():
    jsonArray = []
      
    #read csv file
    with open('paie.csv', encoding='latin-1') as csvf: 
        #load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(csvf) 

        #convert each csv row into python dict
        for row in csvReader: 
            #add this python dict to json array
            jsonArray.append(row)
  
    #convert python jsonArray to JSON String and write to file
    with open('paie.json', 'w', encoding='latin-1') as jsonf: 
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)


###########----FORMAT 2 NOREDDINE---############

#-----------LOAD-----------#
def load(path):
    input_text= extract_text(path)
    f = StringIO(input_text)
    mylist = (f.getvalue())
    mylist = mylist.split("\n")
    return (mylist)



#----------INDEX----------#
#ursaff divisé en 5 parties
def ursaff1(mylist):
    #URSSAFF
    urssaf01i = mylist.index('Base Contribution solidarité autonomie')
    urssaf01_1= (mylist[urssaf01i+19:urssaf01i+42])
    return urssaf01_1
    
def ursaff2(mylist):
    urssaf01_2i = mylist.index('CSG déductible (TOT)')
    urssaf01_2 = (mylist[urssaf01_2i+4:urssaf01_2i+19])
    return urssaf01_2


def ursaff3(mylist):
    urssaf01_2i = mylist.index('CSG déductible (TOT)')
    urssaf01_3 = (mylist[urssaf01_2i+38:urssaf01_2i+41])
    return urssaf01_3

def ursaff4(mylist):
    urssaf01_2i = mylist.index('CSG déductible (TOT)')
    urssaf01_4 = (mylist[urssaf01_2i+48:urssaf01_2i+51])
    return urssaf01_4
    
    
def ursaff5(mylist):
    urssaf01_5i = mylist.index('Net à payer')
    urssaf01_5 = (mylist[urssaf01_5i+11:urssaf01_5i+14])
    return urssaf01_5

def retraite1(mylist):
    #Retraite complémentaire 
    retraite01_1i = mylist.index('CSG déductible (TOT)')
    retraite01 = (mylist[retraite01_1i+19:retraite01_1i+23])
    return retraite01
    
def mutuelle1(mylist):
    #mutuelle
    mutuelle01_1i = mylist.index('CSG déductible (TOT)')
    mutuelle01 = (mylist[mutuelle01_1i+27:mutuelle01_1i+38])
    return mutuelle01
    
def taxe1(mylist): 
    #taxe 
    taxe01_i = mylist.index('CSG déductible (TOT)')
    taxe01 = (mylist[taxe01_i+41:taxe01_i+47])
    return taxe01

#nom
def nom1(mylist):
    nom_i= mylist.index("FICHES  INDIVIDUELLES  DETAILLEES")
    nom = (mylist[nom_i+9])
    return nom

#----------SOMME DANS MEME CATEGORIE--------------#
def sub_sum(liste): #additionne une même liste 
    #replace , by . to convert str to float 
    prov = []
    for i in liste: 
        if i != ' ':
            a = i.replace(",", ".")
            prov.append(a)

    #remove space, else we can't convert str to float 
    prov2 = []
    for i in prov:     
            a = i.replace(" ", "")
            prov2.append(a)

    #convert list str to float list 
    liste=([float(x) for x in prov2])
    
    #sub sum
    liste=sum(liste)
    
    return(liste)



#----------CONVERT TO CSV-----------#

def convert_csv(URSSAF,retraite_complémentaire,mutuelle_prévoyance,taxe_app_et_formation_pro):
    
    df = pd.DataFrame(columns=['mois','urssaf','retraite_complementaire','mutuelle','taxe_formation'])
    new = {'mois': "janvier", 'urssaf': URSSAF,'retraite_complementaire':retraite_complémentaire,'mutuelle':mutuelle_prévoyance,'taxe_formation': taxe_app_et_formation_pro}
    df =df.append(new, ignore_index=True)
    
    

    field_names = ['mois','urssaf','retraite_complementaire','mutuelle','taxe_formation']

    with open('paieF2.csv', 'a+', newline ='') as f_object:
        csv_writer = DictWriter(f_object,fieldnames=field_names )
        if f_object.tell() == 0:
                csv_writer.writeheader()
        csv_writer.writerow(new) 
        f_object.close()
    
    return df


###########-----------------------------------CV -----------------------------################


#------------ CREATION FILE TXT ET CHARGEMENT ------------#

def extract_content(pdf_path):
    input_text=  extract_text(pdf_path)
    input_text = input_text.lower()
    f = StringIO(input_text)
    file_content = (f.getvalue())
    return file_content

    
#------------ NETTOYAGE DONNEES ------------#
def normalisation(file_content):
    ##TOKENIZATION : #coupe en mot, exception de ponctuation pour c+ ou c#
    tokenizer = nltk.word_tokenize(file_content, language='french')
    tokenizer = [word.lower() for word in tokenizer
                         if word not in ['\'','/','|',',', '’','//', '”', '“', '?', '!',':',';','...','[]','()','(',')']]


    mwtokenizer = nltk.MWETokenizer(separator='')
    mwtokenizer.add_mwe(('c', '#'))
    mwtokenizer.add_mwe(('c', '+'))
    mwtokenizer.add_mwe(('j','.'))
    mwtokenizer.add_mwe(('j','-'))

    tokens =mwtokenizer.tokenize(tokenizer)
    #print(tokens)

    ##STOPWORDS : enleve mots non nécessaires, exception
    stopword = set(nltk.corpus.stopwords.words('french'))
    exclude_words = set(("c+","c#",'c','js.node')) 
    stop_words = stopword - exclude_words

    stopword = stopwords.words('french')
    removing_stopwords = [word for word in tokens if word not in stop_words]  

    #LEMMITAZION: veut dire met un mot à sa forme pritimive comme les verbes 
    wordnet_lemmatizer = WordNetLemmatizer() 
    lemmatized_word = [wordnet_lemmatizer.lemmatize(word) for word in removing_stopwords]
    #print(lemmatized_word)
    while '\n' in lemmatized_word:      
        lemmatized_word.remove('\n')
        
    return lemmatized_word 


#------------ EXTRACTION SKILLS ------------#

def extract_skills(lemmatized_word):
    #LIST 
    skills = ['sql','machine learning','c+','c#','c','data science','python','word','excel','English','mysql','java','html','plm','css','javascript','scrums/safe','jquery','react.js','php','node.js']
    new_skills = []

    for i in skills:
        for j in lemmatized_word :
            if (i==j):
                new_skills.append(j)
                #print(i)
                


    #new_skills = list(new_skills.split(" "))
    new_skills = list(dict.fromkeys(new_skills)) #enlever les doublons
    #new_skills = ", ".join(new_skills) #list to str
    print('\ncompétences extraites: ',new_skills)
    
    return new_skills


#------------ EXTRACTION LANGUES ------------#

def extract_langues(lemmatized_word):
    #LIST
    langue = ['français','anglais','arabe','espagnol','espanol','italien','russe', 'allemand']
    new_langues = []

    for i in langue:
        for j in lemmatized_word :

            if (i==j):
                new_langues.append(j)


    new_langues = list(dict.fromkeys(new_langues))
    #new_langues = ", ".join(new_langues) #list to str 
    print('langues:',new_langues)
    
    return new_langues


#------------ EXTRACTION MAIL ------------#
def mail(file_content):
    r = re.search(".*@.*", file_content)
    r =r.group()
    r = r.split()
    for i in r :
        r = re.search(".*@.*", i)
        if r :
            r = r.group()
            print('email:', r)
            return r


#------------ CONVERSION CSV------------#

    
def convert_to_csv(new_skills, new_langues, r):   
    #AJOUT DANS DATAFRAME  
    df = pd.DataFrame(columns=['Langue','Competence','Mail','Profil'])
    new = {'Langue':new_langues, 'Competence': new_skills, 'Mail': r, 'Adresse':'4 rue pasteur le kremlin','Profil':'ingenieur' }
    df =df.append(new, ignore_index=True)
    

    #CREATION CSV  
    #skill= { 'Langue': new_langues, 'Competence': new_skills, 'Mail': r, 'Adresse':'35 Rue raymond peynet longjumeau,'Profil':'consultant'}
    field_names = ['Langue','Competence','Mail', 'Adresse', 'Profil']

   

    with open('cv.csv', 'a+', newline ='') as f_object:
        csv_writer = DictWriter(f_object,fieldnames=field_names )
        if f_object.tell() == 0:
                csv_writer.writeheader()
        csv_writer.writerow(new) 
        f_object.close()
    
    return df



  


#-----------------------------------MAIN--------------------------------#
    
def main():
    choix = st.sidebar.selectbox('Choisis le format',['','fiche de paie 1-RH','fiche de paie 2-Noreddine', 'CV'])
   
    if choix == '':
        st.title('Extraction des données ETIXWAY')
        st.subheader('1 - Choisis quel fichier extraire: bulletin de paie ou CV? ')
        st.subheader('2 - Entre le directory du dossier où sont stockés tes fichiers à extraire très important')
        st.subheader('3 - Upload ton fichier, le csv final sera enregistré dans le directory entré ')

    if choix =='fiche de paie 1-RH':
        st.title ('Telecharge fiche de paie format 1 :page_facing_up:')

        dir =st.text_input(label= 'entre le chemin du directory de tes fichiers à extraire:', placeholder='C:\\Users\\nom\\...\\...')
        if dir:
            os.chdir(dir)  

        multiple = st.sidebar.selectbox('Choisis ta méthode d\'extraction',['single file', 'multiple files'])
        if multiple == 'single file':
            uploaded_file = st.file_uploader('extraction du nom, location, mois, net, total - fichier un par un', type=['pdf'], accept_multiple_files=False)
            if uploaded_file is not None:
                    path = os.path.abspath(uploaded_file.name)
                    input_text = get_pdf_file_content(path)
                    create_extract_file(input_text)
                    csv_to_json()
                    if os.path.isfile('paie.csv'):
                        st.success ("csv crée: paie.csv")
                    else:
                        st.error ("le csv n'a pas été crée")
                    
                    if os.path.isfile('paie.json'):
                        st.success ("JSON crée: paie.json")
                    else:
                        st.error ("le json n'a pas été crée")
                    
                    df = pd.read_csv('paie.csv', encoding = 'latin-1')
                    a= count(df)
                    st.write(a, 'nombres de fichiers extraits')
                    st.table(df)
                    csv =os.path.abspath('paie.csv')
                    st.write('les fichiers csv et json ont été sauvegardé dans:')
                    st.text(csv)

        if multiple == 'multiple files':

            uploaded_file = st.file_uploader('extraction du nom, location, mois, net, total - multiples fichiers à la fois', type=['pdf'], accept_multiple_files=True)
            if uploaded_file is not None:
                for files in uploaded_file: #[file1, file2]
                    path = os.path.abspath(files.name)
                    input_text = get_pdf_file_content(path)
                    create_extract_file(input_text)
                    csv_to_json()
                    if files == uploaded_file[-1]:
                        if os.path.isfile('paie.csv'):
                            st.success ("csv crée: paie.csv")
                        else:
                            st.error ("le csv n'a pas été crée")
                        
                        if os.path.isfile('paie.json'):
                            st.success ("JSON crée: paie.json")
                        else:
                            st.error ("le json n'a pas été crée")
                
                        df = pd.read_csv('paie.csv', encoding = 'latin-1')
                        st.table(df)
                        csv =os.path.abspath('paie.csv')
                        st.write('les fichiers csv et json ont été sauvegardé dans:')
                        st.text(csv)

#--------------------------------#
                
    if choix == 'fiche de paie 2-Noreddine':
        st.title ('Telecharge fiche de paie format 2 :page_facing_up:')

        dir =st.text_input(label= 'entre le chemin du directory de tes fichiers à extraire:', placeholder='C:\\Users\\nom\\...\\...')
        if dir:
            os.chdir(dir)  
      

        uploaded_file = st.file_uploader('extraction de URSSAF, retraite complémentaire, mutuelle & prévoyance,taxe & formation pro', type=['pdf'], accept_multiple_files=False)
        if uploaded_file is not None:
                path = os.path.abspath(uploaded_file.name)
                mylist = load(path)
                ursaf01_1 = ursaff1(mylist)
                ursaf01_2= ursaff2(mylist)
                ursaf01_3= ursaff3(mylist)
                ursaf01_4= ursaff4(mylist)
                ursaf01_5 = ursaff5(mylist)
                retraite = retraite1(mylist)
                mutuelle = mutuelle1(mylist)
                taxe = taxe1(mylist)
                #print(ursaf01_1,'\n',ursaf01_2,'\n',ursaf01_3,'\n',ursaf01_4,'\n',ursaf01_5,'\n',retraite,'\n',mutuelle,'\n',taxe)
                a = sub_sum(ursaf01_1)
                b = sub_sum(ursaf01_2)
                c = sub_sum(ursaf01_3)
                d = sub_sum(ursaf01_4)
                e = sub_sum(ursaf01_5)
                f = sub_sum(retraite)
                g = sub_sum(mutuelle)
                h = sub_sum(taxe)
                
                #print(a,'\n',b,'\n',c,'\n',d,'\n',e,'\n',f,'\n',g,'\n',h)
                URSSAF = a+b+c+d+e
                retraite_complémentaire= f
                mutuelle_prévoyance = g
                taxe_app_et_formation_pro = h
                nom = nom1(mylist)
                st.write('nom: ',nom)
                st.write('URSSAF: ', URSSAF)
                st.write('retraite complémentaire: ',retraite_complémentaire)
                st.write('mutuelle: ', mutuelle_prévoyance)
                st.write('taxe et formation: ', taxe_app_et_formation_pro)
                df = convert_csv(URSSAF,retraite_complémentaire,mutuelle_prévoyance,taxe_app_et_formation_pro)
                if os.path.isfile('paieF2.csv'):
                    st.success ("csv crée: paieF2.csv")
                else:
                    st.error ("le csv n'a pas été crée")
    
                csv =os.path.abspath('paieF2.csv')
                st.table(df)
                st.write('le fichier csv a été sauvegardé dans:' )
                st.text(csv)
                
#------------------------#
    if choix =='CV':

        st.title ('Telecharge le CV :page_facing_up:')
        a =st.text_input('entre le chemin du directory de tes fichiers à extraire')
        if a :
            os.chdir(a)  
        

        uploaded_file = st.file_uploader('extraction des compétences, langues, email', type=['pdf'], accept_multiple_files=False)
        if uploaded_file is not None:
            path = os.path.abspath(uploaded_file.name)
            file_content = extract_content(path)
            lemmatized_word = normalisation(file_content)
            skills = extract_skills(lemmatized_word)
            langue = extract_langues(lemmatized_word)
            email = mail(file_content)
            df = convert_to_csv(skills,langue, email)
            if os.path.isfile('cv.csv'):
                st.success ("csv crée: cv.csv")
            else:
                st.error ("le csv n'a pas été crée")

            csv =os.path.abspath('cv.csv')
            st.table(df)
            st.write('le fichier csv a été sauvegardé dans:' )
            st.text(csv)




    
if __name__ == "__main__":
    main()


#pas d'ajout de multiples files 
#pas de choix de nom du csv ni du json 
#peut rajouter le même fichier 
