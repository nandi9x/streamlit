import os
import streamlit as st 
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import pandas as pd 
import csv
from csv import DictWriter
import json 
from pathlib import Path


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
    st.write(mylist)
  


     
    #Extraction mots 
    date_index = mylist.index("Paye du : ")
    a= (mylist[date_index+1])
    b=  str(a).strip('[]') #list to str pour prendre substring
    mois=(b[3:5])
 
    i = mylist.index("FONTENAY-SOUS-BOIS ")
    nom = (mylist[i+5])
    index_nom = mylist.index(nom) #chercher l'index du nom 
    
    adresse_index = mylist.index("RUBRIQUES ")
    adresse = (mylist[index_nom+1:adresse_index-2]) #va donner plusieurs items d'une liste
    adresse = " ".join(adresse) #pour affichage meilleur 
    
    net_index = mylist.index('NET PAYE EN EUROS ')
    net= mylist[net_index+2]

    total_index= mylist.index('CONGES ')
    total = (mylist[total_index-1])

#------------ CREATION CSV ------------#

    new = {'Mois': mois, 'Nom': nom, 'Adresse': adresse,'Net_paye':net, 'Total_verse':total}
    field_names = ['Mois','Nom','Adresse','Net_paye','Total_verse']

    with open('paie.csv', 'a+', newline ='', encoding = 'utf-8') as f_object:
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
        
        
def main():

   # os.chdir(r'C:\Users\ypyea\Documents\Nanda\EFREI\stage M1\jupyter notebook\bulletin de paie') ##naviguer dans ce répertoire 
   

    st.title ('Upload your payslip :page_facing_up:')

    uploaded_file = st.file_uploader('extract name, location, month, net, total', type=['pdf'], accept_multiple_files=False)
    if uploaded_file is not None:
            input_text = get_pdf_file_content(uploaded_file.name)
            create_extract_file(input_text)
            csv_to_json()
            st.header(' création de "paie.csv" et "paie.json" ')
            df = pd.read_csv('paie.csv', encoding = 'utf-8')
            with open("paie.csv", "rb") as file:
            
                st.download_button(label='download',data = file, file_name='paie.csv')
            file.close()
                             

           
            a = os.path.abspath("paie.csv")
            st.write(a)  

            st.table(df)
            

    
if __name__ == "__main__":
    main()


#pas d'ajout de multiples files 
#pas de choix de nom du csv ni du json 
#peut rajouter le même fichier 
