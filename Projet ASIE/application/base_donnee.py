# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 21:37:55 2020

@author: rapha
"""

from zipfile import ZipFile
import json
import re
import sqlite3
import os

def get_info(country,continent):
    with ZipFile('{}.zip'.format(continent),'r') as z :
        return json.loads(z.read('{}.json'.format(country)))
    
def get_name(country,info):
    if country=='Kazakhstan':
        return 'Republic of Kazakhstan'
    if country=='Nepal':
        return 'Federal Democratic Republic of Nepal'
    if country=='Singapore':
        return 'Republic of Singapore'
    if country=='Sri_Lanka':
        return 'Sri Lanka'
    if 'conventional_long_name' in info :
        return info['conventional_long_name']
    else :
        return False


def get_capital(country,info):
    if country=='State_of_Palestine':
        return 'Jerusalem'
    if country=='Brunei':
        return 'Bandar Seri Begawan'
    if country=='Cambodia':
        return 'Phnom Penh'

    capital=info['capital']
    m=re.match("\[\[(\w+)\]\]",capital)
    if m :
        return m.group(1)
    else :
        if country=='India':
            return 'New Delhi'
        if country=='Kazakhstan':
            return 'Noursoultan'
        if country=='Kuwait':
            return 'Koweit'
        if country=='Malaysia':
            return 'Kuala Lumpur'
        if country=='Oman':
            return 'Mascate'
        if country=='Singapore':
            return 'Quora'
        if country=='Sri_Lanka':
            return 'Sri Jayawardenepura Kotte'
        if country=='United_Arab_Emirates':
            return 'Abou Dabi'
        if country=='Yemen':
            return 'Sanaa'

def get_coords(nom_pays,info):
    if nom_pays=='Malaysia':
        return {'lat':3+8/60,'long':101+41/60}
    if nom_pays=='Maldives':
        return {'lat':4+10/60,'long':73.5}
    if nom_pays=='Philippines':
        return {'lat':14+35/60,'long':120+59/60}
    if nom_pays=='State_of_Palestine':
        return {'lat':31+46/60,'long':35+11/60}
    if nom_pays=='Yemen':
        return {'lat':15+21/60,'long':44+12/60}
    coo=info['coordinates']
    m=re.match('\{\{Coord\s*\|(\d+)\|(\d+)\|?\d*\|(\w)\|(\d+)\|(\d+)\|?\d*\|(\w)\|.*',coo) #choix de ne pas retenir les secondes car elles ne sont que peu précisées en général
    if m!= None :
        if m.group(3)=="S":
            lat=-int(m.group(1))-int(m.group(2))/60
        else :
            lat=int(m.group(1))+int(m.group(2))/60
        if m.group(6)=="E":
            long=int(m.group(4))+int(m.group(5))/60
        else :
            long=-int(m.group(4))-int(m.group(5))/60
    else :
        if nom_pays=='Bhutan':
            lat=27+28/60+1/3600
            long=89+38/60+16/3600
        if nom_pays=='Brunei':
            lat=4+53/60+27/3600
            long=114+56/60+28/3600
        if nom_pays=='East_Timor':
            lat=-8-33/60-31/3600
            long=125+34/60+25/3600
        if nom_pays=='Indonesia':
            lat=-6-12/60-53/3600
            long=106+50/60+42/3600
        if nom_pays=='Israel':
            lat=31+47/60
            long=35+13/60
        if nom_pays=='Mongolia':
            lat=47+55/60
            long=106+55/60
        if nom_pays=='Taiwan':
            lat=25+5/60
            long=121+33/60
        if nom_pays=='Turkey':
            lat=41+44/3600
            long=28+58/60+34/3600
        
    return {'lat':lat,'long':long}

def get_cctld(info):
    cctld=info['cctld']
    cctld=cctld.split('[')[-1].split(']')[0]
    return(cctld)

def get_currency(info):
    currency=info['currency']
    currency=currency.split('[')[-1].split(']')[0]
    return(currency)
    
def get_area(info):
    area=info['area_km2'].split('-')[0]
    return(area)
    
def get_drive_side(info):
    drive=info['drives_on']
    drive=drive.split('[')[-1].split(']')[0].split('#')[0].split('|')[0]
    return(drive)

def get_calling_code(nom_pays,info):
    if info['common_name']=='Brunei':
        calling_code='+673'
    else :
        calling_code=info['calling_code']
        m=re.match('\[\[\D*(\d+)\]\]\.*',calling_code)
        if m :
            calling_code='+'+ m.group(1)
        else :
            if nom_pays=='Brunei':
                calling_code='+673'
            if nom_pays=='Israel':
                calling_code='+972'
            if nom_pays=='Kazakhstan':
                calling_code='+7'
            if nom_pays=='Qatar':
                calling_code='+974'
    return(calling_code)

def get_lien_image(nom_pays,lien):
    liste=os.listdir(lien)
    print(1)
    nombre_lettre=len(nom_pays)
    longueur_liste=len(liste)
    pays_minuscule=nom_pays.lower()
    print(2)
    pays=None
    i=0
    while pays==None and i<longueur_liste:
        if liste[i][:nombre_lettre]==pays_minuscule :
            pays=liste[i]
            print(3)
        i+=1
    print(4)
    return pays

   
def save_country(conn,country,info,compteur,lien): #conn='str' lien de la base de donnée, country='str' , info='dic' infobox , 'compteur', 'lien'=lien du document contenant les drapeaux
    c=connex.cursor() 
    sql='INSERT INTO countries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)'
    name=get_name(country,info)
    capital=get_capital(country,info)
    coords=get_coords(country,info)
    continent='asia'
    idc=compteur
    cctld=get_cctld(info)
    currency=get_currency(info)
    area=get_area(info)
    drive_side=get_drive_side(info)
    calling_code=get_calling_code(country,info)
    image=get_lien_image(country,lien)
    c.execute(sql,(country,name,capital,coords['lat'],coords['long'],continent,idc,cctld,currency,area,drive_side,calling_code,image))
    connex.commit()



def read_country(connex,country): #necessite au préalable d'ouvrir la connexion sql sur connex
    c=connex.cursor()
    sql='SELECT * FROM countries WHERE wp=?'
    c.execute(sql,(country,))
    requete=c.fetchall()
    #d=conn.cursors()
    #requete=c.execute("PRAGMA table_info(countries);")
    return requete


def get_liste_pays(continent):
    with ZipFile('{}.zip'.format(continent),'r') as z :
        #liste des pays contenus de le fichier
        return z.namelist()

def update_country_continent(conn,country,continent):
    
    # preparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET continent=? WHERE wp=?'

    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(continent,country))
    conn.commit()
    conn.close()
   
def update_country_driving_side(conn,country,drives_on):
    # preparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET drives_on=? WHERE wp=?'

    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(drives_on,country))
    conn.commit()

def update_country_coordonnees(conn,country,latitude,longitude):
    
    # preparation de la commande SQL
    c = conn.cursor()
    sql = 'UPDATE countries SET latitude=?,longitude=? WHERE wp=?'

    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(latitude,longitude,country))
    conn.commit()
    
def update_image(conn,country,lien):
    liste=os.listdir(lien)
    nombre_lettre=len(country)
    longueur_liste=len(liste)
    pays_minuscule=country.lower()
    pays=None
    i=0
    while pays==None and i<longueur_liste:
        if liste[i][:nombre_lettre]==pays_minuscule :
            pays=liste[i]
        i+=1
    c=conn.cursor()
    sql='UPDATE countries SET image=? WHERE wp=?'
    c.execute(sql,(pays,country))
    conn.commit()
    
    
# création de la base
conn='countries.sqlite'
  
base=1
if base==1: 
    connex=sqlite3.connect(conn)
    block=0
    compteur=1
    for c in get_liste_pays('asia'):
        c=c[:-5]
        if c=='Afghanistan':
            block=1
        if block==1:
            info=get_info(c,'asia')
            print(conn,c)
            save_country(conn,c,info,compteur,"C:/Users/rapha/Documents/Centrale Lyon/informatique/projet d application/projet/client/flags")
            compteur+=1
    connex.close()
    