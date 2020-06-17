# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 11:19:20 2020

@author: Vincent Fendel
"""

################################Les imports ###################################

import re
from zipfile import ZipFile
import json
import sqlite3
###############################################################################

conn = sqlite3.connect('pays.sqlite')

## On souhaite créer une table ds sql permettant de récupérer facilement les 
# données des payes suivantes : continent, nom du pays, capitale latitude,
# longitude, le drapeau ( nom du fichier image),nom du domaine internet,
# la monnaie, la surface, le coté de criculation,  le préfixe téléphonique 
# international, le titre et le nom du leader principal, le type de 
# gouvernement du pays,des informations sur le PIB et le PIB par habitant,
# informations sur la démographie (pop et année du recensement).

def get_zip_info(country,continent):
    with ZipFile('{}.zip'.format(continent),'r') as z:
    
        # infobox du pays
        return json.loads(z.read('{}'.format(country)))
    
def print_capital(info):
    print('{}, Capital : {} - {}'.format(info['conventional_long_name'],info['capital'],info['coordinates']))
    
zw = get_zip_info('Zimbabwe','africa')   
print_capital(zw)
    
#zw = get_zip_info('Zimbabwe','africa')
#capital = zw['capital']
#print('Chaîne brute : {}'.format(capital))
## Analyse de la chaîne brute en la comparant à [[*]], et en mémorisant le contenu des crochets
#m = re.match("\[\[(\w+)\]\]", capital)
#
#capital = m.group(1)
#print('Capitale : {}'.format(capital))


def get_name(wp_info):
    if 'conventional_long_name' in wp_info:
        name = wp_info['conventional_long_name']
        return name
    
    if 'common_name' in wp_info and wp_info['common_name'] == 'Singapore':
        return 'Republic of Singapore'
    
        # S'applique uniquement au Vanuatu  
    if 'common_name' in wp_info:
        name = wp_info['common_name']
        print( 'using common name {}...'.format(name),end='')
        return name
    
    print('Could not fetch country name : {}'.format(wp_info))
    return None


# Récupération de la capitale d'un pays depuis l'infobox 
#
def get_capital(wp_info):
    #cas général
    if 'capital' in wp_info:
        capital = wp_info['capital'].replace('\n',' ')
       
        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",capital)
        capital = m.group(1)
        return capital
    print('Could not fetch country capital : {}'.format(wp_info))
    return None

#
# Récupération des coordonnées de la capitale depuis l'infobox d'un pays
#
#
# Récupération des coordonnées de la capitale depuis l'infobox d'un pays
#
def get_coords(wp_info):

    # S'il existe des coordonnées dans l'infobox du pays
    # (cas le plus courant)
    if 'coordinates' in wp_info:

        # (?i) - ignorecase - matche en majuscules ou en minuscules
        # ça commence par "{{coord" et se poursuit avec zéro ou plusieurs
        #   espaces suivis par une barre "|"
        # après ce motif, on mémorise la chaîne la plus longue possible
        #   ne contenant pas de },
        # jusqu'à la première occurence de "}}"
        m = re.match('(?i).*{{coord\s*\|([^}]*)}}', wp_info['coordinates'])

        # l'expression régulière ne colle pas, on affiche la chaîne analysée pour nous aider
        # mais c'est un aveu d'échec, on ne doit jamais se retrouver ici
        if m == None :
            print(' Could not parse coordinates info {}'.format(wp_info['coordinates']))
            return None

        # cf. https://en.wikipedia.org/wiki/Template:Coord#Examples
        # on a récupère une chaîne comme :
        # 57|18|22|N|4|27|32|W|display=title
        # 44.112|N|87.913|W|display=title
        # 44.112|-87.913|display=title
        str_coords = m.group(1)

        # on convertit en numérique et on renvoie
        if str_coords[0:1] in '0123456789':
            return cv_coords(str_coords)
        
    # Aveu d'échec, on ne doit jamais se retrouver ici
    print(' Could not fetch country coordinates')
    return None
    
####################
# La fonction cv_coords

#
# Conversion d'une chaîne de caractères décrivant une position géographique
# en coordonnées numériques latitude et longitude
#
def cv_coords(str_coords):
    # on découpe au niveau des "|" 
    c = str_coords.split('|')

    # on extrait la latitude en tenant compte des divers formats
    lat = float(c.pop(0))
    if (c[0] == 'N'):
        c.pop(0)
    elif ( c[0] == 'S' ):
        lat = -lat
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'N' ):
        lat += float(c.pop(0))/60
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'S' ):
        lat += float(c.pop(0))/60
        lat = -lat
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'N' ):
        lat += float(c.pop(0))/60
        lat += float(c.pop(0))/3600
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'S' ):
        lat += float(c.pop(0))/60
        lat += float(c.pop(0))/3600
        lat = -lat
        c.pop(0)

    # on fait de même avec la longitude
    lon = float(c.pop(0))
    if (c[0] == 'W'):
        lon = -lon
        c.pop(0)
    elif ( c[0] == 'E' ):
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'W' ):
        lon += float(c.pop(0))/60
        lon = -lon
        c.pop(0)
    elif ( len(c) > 1 and c[1] == 'E' ):
        lon += float(c.pop(0))/60
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'W' ):
        lon += float(c.pop(0))/60
        lon += float(c.pop(0))/3600
        lon = -lon
        c.pop(0)
    elif ( len(c) > 2 and c[2] == 'E' ):
        lon += float(c.pop(0))/60
        lon += float(c.pop(0))/3600
        c.pop(0)
    
    # on renvoie un dictionnaire avec les deux valeurs
    return {'lat':lat, 'lon':lon }



# votre code ici


#print(read_country(conn,'Zimbabwe'))


def get_cctld(wp_info):
    #cas général
    if 'cctld' in wp_info:
        cctld = wp_info['cctld'].replace('\n',' ')
       
        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",cctld)
        cctld = m.group(1)
        return cctld
    print('Could not fetch country capital : {}'.format(wp_info))
    return None

def get_currency(wp_info):
    #cas général
    if 'currency' in wp_info:
        currency = wp_info['currency'].replace('\n',' ')
       
        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",currency)
        currency = m.group(1)
        res = currency.split('|')
        return res[0]
    print('Could not fetch country capital : {}'.format(get_name(wp_info)))
    return None

def get_area_km2(wp_info):
    #cas général
    if 'area_km2' in wp_info:
        area_km2 = wp_info['area_km2'].replace('\n',' ')
       
#        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",area_km2)
#        area_km2 = m.group(1)
        return area_km2
    print('Could not fetch country capital : {}'.format(get_name(wp_info)))
    return None

def get_drives_on(wp_info):
    #cas général
    if 'drives_on' in wp_info:
        drives_on = wp_info['drives_on'].replace('\n',' ')
       
        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",drives_on)
        if m == 'NoneType':
            return drives_on
        else :
            drives_on = m.group(1)
        return drives_on
    print('Could not fetch country capital : {}'.format(get_name(wp_info)))
    return None

def get_calling_code(wp_info):
    #cas général
    if 'calling_code' in wp_info:
        calling_code = wp_info['calling_code'].replace('\n',' ')
        nums = re.findall('\d+', calling_code)
        nums1 = []
        for i in nums:
            nums1.append('+'+i)
        elem = ''
        for i in range(len(nums1)):
            if i ==0:
                elem += nums1[i]
            else :
                elem += ','+nums1[i]
        return elem
    print('Could not fetch country capital : {}'.format(get_name(wp_info)))
    return None

#stri = 'gege+12+25'
#
#def test(stri):
#    var_nb = re.findall('\d+', stri)
#    var_nb1 = []
#    for i in var_nb:
#        var_nb1.append('+'+i)
#    elem = ''
#    for i in range(len(var_nb1)):
#        if i ==0:
#            elem += var_nb1[i]
#        else:
#            elem += ','+var_nb1[i]
#    return elem




def get_leader_title(wp_info):
    #cas général
    if 'leader_title' in wp_info:
        leader_title = wp_info['leader_title'].replace('\n',' ')
       
        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",leader_title)
        leader_title = m.group(1)
        return leader_title
    if 'leader_title1' in wp_info:
        leader_title1 = wp_info['leader_title1'].replace('\n',' ')
       
        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",leader_title1)
        leader_title1 = m.group(1)
        
        Separateur = leader_title1.split('|')
        if len(Separateur)>1:
            return Separateur[0]
        else : 
            return leader_title1
    print('Could not fetch country capital : {}'.format(get_name(wp_info)))
    return None

def get_leader_name(wp_info):
    #cas général
    if 'leader_name' in wp_info:
        leader_name = wp_info['leader_name'].replace('\n',' ')
       
        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",leader_name)
        leader_name = m.group(1)
        return leader_name
    if 'leader_name1' in wp_info:
        leader_name1 = wp_info['leader_name1'].replace('\n',' ')
       
        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",leader_name1)
        leader_name1 = m.group(1)
        return leader_name1
    print('Could not fetch country capital : {}'.format(get_name(wp_info)))
    return None

def get_government_type(wp_info):
    #cas général
    if 'government_type' in wp_info:
        government_type = wp_info['government_type'].replace('\n',' ')
       
        m = re.match(".*?\[\[([|\w\s',|(.)|-]+)|\]\]",government_type)
        government_type = m.group(1)
        sep = government_type.split('|')
        return sep[0]
    print('Could not fetch country capital : {}'.format(get_name(wp_info)))
    return None

def get_GDP_nominal(wp_info):
    #cas général
    if 'GDP_nominal' in wp_info:
        GDP_nominal = wp_info['GDP_nominal'].replace('\n',' ')
       
#        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",GDP_nominal)
#        GDP_nominal = m.group(1)
        return GDP_nominal
    print('Could not fetch country capital : {}'.format(get_name(wp_info)))
    return None

def get_GDP_nominal_year(wp_info):
    #cas général
    if 'GDP_nominal_year' in wp_info:
        GDP_nominal_year = wp_info['GDP_nominal_year'].replace('\n',' ')
       
#        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",GDP_nominal_year)
#        GDP_nominal_year = m.group(1)
        return GDP_nominal_year
    print('Could not fetch country capital : {}'.format(get_name(wp_info)))
    return None

def get_GDP_nominal_per_capita(wp_info):
    #cas général
    if 'GDP_nominal_per_capita' in wp_info:
        GDP_nominal_per_capita = wp_info['GDP_nominal_per_capita'].replace('\n',' ')
       
#        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",GDP_nominal_per_capita)
#        GDP_nominal_per_capita = m.group(1)
        return GDP_nominal_per_capita
    print('Could not fetch country capital : {}'.format(get_name(wp_info)))
    return None

def get_population_census(wp_info):
    #cas général
    if 'population_census' in wp_info:
        population_census = wp_info['population_census'].replace('\n',' ')
       
#        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",population_census)
#        population_census = m.group(1)
        return population_census
    if 'population_estimate' in wp_info:
        population_census = wp_info['population_estimate'].replace('\n',' ')
       
#        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",population_census)
#        population_census = m.group(1)
        return population_census
    
    print('Could not fetch country capital : {}'.format(get_name(wp_info)))
    return None

def get_population_census_year(wp_info):
    #cas général
    if 'population_census_year' in wp_info:
        population_census_year = wp_info['population_census_year'].replace('\n',' ')
       
#        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",population_census_year)
#        population_census_year = m.group(1)
        return population_census_year
    if 'population_estimate_year' in wp_info:
        population_estimate_year = wp_info['population_estimate_year'].replace('\n',' ')
       
#        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",population_estimate_year)
#        population_estimate_year = m.group(1)
        return population_estimate_year
    
    print('Could not fetch country capital : {}'.format(get_name(wp_info)))
    return None

def get_flag(wp_info):
    #cas général
    if 'flag' in wp_info:
        flag = wp_info['flag'].replace('\n',' ')
       
#        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",flag)
#        flag = m.group(1)
        return flag
    if 'image_flag' in wp_info:
        image_flag = wp_info['image_flag'].replace('\n',' ')
       
#        m = re.match(".*?\[\[([\w\s',(.)|-]+)\]\]",image_flag)
#        image_flag = m.group(1)
        return image_flag
    print('Could not fetch country capital : {}'.format(wp_info))
    return None



def recup_info_continent(continent):   
    nom_fichier = '{}.zip'.format(continent)
    with ZipFile(nom_fichier,'r') as z:
        
        # liste des documents contenus dans le fichier zip
#        print(z.namelist())
#        print()
        L = z.namelist()
        return L
        # infobox de l'un des pays
#        info = json.loads(z.read('China.json'))
#        print(info)




paysAsie = recup_info_continent('asia')
paysAfrique = recup_info_continent('africa')
paysEurope = recup_info_continent('europe')
paysAmNord = recup_info_continent('north_america')
paysOceanie = recup_info_continent('oceania')
paysAmSud = recup_info_continent('south_america')

    
    
    
    
###############################################################################
# ECRITURE DANS LA BDD SQL    
    
    
def save_country(conn,country,info,conti):
    
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'INSERT OR REPLACE INTO countries VALUES (?, ?, ?, ?, ?,?,?, ?, ?, ?, ?,?,?, ?, ?, ?, ?,?,?,?)'
    
    # les infos à enregistrer
    name = get_name(info)
    capital = get_capital(info)
    coords = get_coords(info)
    continent = conti
    cctld = get_cctld(info)
    currency = get_currency(info)
    area_km2 = get_area_km2(info)
    drives_on = get_drives_on(info)
    calling_code = get_calling_code(info)
    leader_title = get_leader_title(info)
    leader_name = get_leader_name(info)
    government_type = get_government_type(info)
    GDP_nominal = get_GDP_nominal(info)
    GDP_nominal_year = get_GDP_nominal_year(info)
    GDP_nominal_per_capita = get_GDP_nominal_per_capita(info)
    population_census = get_population_census(info)
    population_census_year = get_population_census_year(info)
    flag = get_flag(info)
    
    # soumission de la commande (noter que le second argument est un tuple)
    c.execute(sql,(country, name, capital, coords['lat'],coords['lon'],continent,
                   cctld,currency,area_km2,drives_on,calling_code,leader_title,leader_name,government_type,GDP_nominal,
                   GDP_nominal_year,GDP_nominal_per_capita,population_census,population_census_year,flag))
    conn.commit()

#save_country(conn,'Zimbabwe',zw)


# On essaie de lire un pays dans la base
def read_country(conn,country):
    
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'SELECT * FROM countries WHERE wp=?'

    # récupération de l'information (ou pas)
    c.execute(sql,(country,))
    r = c.fetchone()
    
    return r
    
    
# ECRITURE
# save_country(conn,'Zimbabwe',zw)
cle = 0
for i in range(len(paysAsie)):
    L = get_zip_info(paysAsie[i],'asia')
    M = get_name(get_zip_info(paysAsie[i],'asia'))
    save_country(conn,M,L,'Asia')
    
    
    
    
    
    
    
    
    
    