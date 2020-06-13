# Projet/serveur.py
#
# Ce serveur correspond à TD3-s7.py amputé de la route /time
#
import http.server
import socketserver
import sqlite3
import json

from urllib.parse import urlparse, parse_qs, unquote


#
# Définition du nouveau handler
#
class RequestHandler(http.server.SimpleHTTPRequestHandler):

  # sous-répertoire racine des documents statiques
  static_dir = '/client'

  # version du serveur
  server_version = 'countries/0.1'

  #
  # On surcharge la méthode qui traite les requêtes GET
  #
  def do_GET(self):
    # on récupère les paramètres
    self.init_params()

    # le chemin d'accès commence par /countries
    if self.path.startswith('/countries'):
      self.send_countries()

    # le chemin d'accès commence par /country et se poursuit par un nom de pays
    elif self.path_info[0] == 'country' and len(self.path_info) > 1:
      self.send_country(self.path_info[1])
      
    # le chemin d'accès commence par /service/countries/...
    elif self.path_info[0] == 'service' and self.path_info[1] == 'countries' and len(self.path_info) > 1:
      #continent = self.path_info[2] if len(self.path_info) > 2 else None
      self.send_json_countries('asia')

    # le chemin d'accès commence par /service/country/...
    elif self.path_info[0] == 'service' and self.path_info[1] == 'country' and len(self.path_info) > 2:
      self.send_json_country(self.path_info[2])
      
      
    elif self.path_info[0] == "location":
      r = self.db_get_countries('asia')
      data = [{k:a[k] for k in a.keys()} for a in r]
      print(data)
      self.send_json(data)
      
    elif self.path_info[0] == "description":
      r = self.db_get_countries('asia') 
      print(1)
      data = [{k:a[k] for k in a.keys()} for a in r]
      for d in data:
        if d['id'] == str(self.path_info[1]):
            print(2)
            self.send_json(d)
            break

    # ou pas...
    else:
      self.send_static()

  #
  # On surcharge la méthode qui traite les requêtes HEAD
  #
  def do_HEAD(self):
    self.send_static()

  #
  # On envoie le document statique demandé
  #
  def send_static(self):

    # on modifie le chemin d'accès en insérant un répertoire préfixe
    self.path = self.static_dir + self.path

    # on appelle la méthode parent (do_GET ou do_HEAD)
    # à partir du verbe HTTP (GET ou HEAD)
    if (self.command=='HEAD'):
        http.server.SimpleHTTPRequestHandler.do_HEAD(self)
    else:
        http.server.SimpleHTTPRequestHandler.do_GET(self)
        

  #     
  # on analyse la requête pour initialiser nos paramètres
  #
  def init_params(self):
    # analyse de l'adresse
    info = urlparse(self.path)
    self.path_info = [unquote(v) for v in info.path.split('/')[1:]]  # info.path.split('/')[1:]
    self.query_string = info.query
    self.params = parse_qs(info.query)

    # récupération du corps
    length = self.headers.get('Content-Length')
    ctype = self.headers.get('Content-Type')
    if length:
      self.body = str(self.rfile.read(int(length)),'utf-8')
      if ctype == 'application/x-www-form-urlencoded' : 
        self.params = parse_qs(self.body)
    else:
      self.body = ''
   
    # traces
    print('path_info =',self.path_info)
    print('body =',length,ctype,self.body)
    print('params =', self.params)


  #
  # On renvoie la liste des pays avec leurs coordonnées
  #
  def send_json_countries(self,continent):

    # on récupère la liste de pays depuis la base de données
    r = self.db_get_countries(continent)

    # on renvoie une liste de dictionnaires au format JSON
    data = [ {k:a[k] for k in a.keys()} for a in r]
    json_data = json.dumps(data, indent=4)
    headers = [('Content-Type','application/json')]
    self.send(json_data,headers)

  def send_json(self,data,headers=[]):
     body = bytes(json.dumps(data),'utf-8') # encodage en json et UTF-8
     self.send_response(200)
     self.send_header('Content-Type','application/json')
     self.send_header('Content-Length',int(len(body)))
     [self.send_header(*t) for t in headers]
     self.end_headers()
     self.wfile.write(body)
  #
  # On renvoie la liste des pays
  #
  def send_countries(self):

    # récupération de la liste des pays dans la base
    r = self.db_get_countries()

    # construction de la réponse
    txt = 'List of all {} countries :\n'.format(len(r))
    n = 0
    for a in r:
       n += 1
       txt = txt + '[{}] - {}\n'.format(n,a[0])
    
    # envoi de la réponse
    headers = [('Content-Type','text/plain;charset=utf-8')]
    self.send(txt,headers)

  #
  # On renvoie les informations d'un pays
  #
  def send_country(self,country):

    # on récupère le pays depuis la base de données
    r = self.db_get_country(country)

    # on n'a pas trouvé le pays demandé
    if r == None:
      self.send_error(404,'Country not found')

    # on génère un document au format html
    else:
      body = '<!DOCTYPE html>\n<meta charset="utf-8">\n'
      body += '<title>{}</title>'.format(country)
      body += '<link rel="stylesheet" href="/TD2-s8.css">'
      body += '<main>'
      body += '<h1>{}</h1>'.format(r['name'])
      body += '<ul>'
      body += '<li>{}: {}</li>'.format('Continent',r['continent'].capitalize())
      body += '<li>{}: {}</li>'.format('Capital',r['capital'])
      body += '<li>{}: {:.3f}</li>'.format('Latitude',r['latitude'])
      body += '<li>{}: {:.3f}</li>'.format('Longitude',r['longitude'])
      body += '</ul>'
      body += '</main>'

      # on envoie la réponse
      headers = [('Content-Type','text/html;charset=utf-8')]
      self.send(body,headers)

  #
  # On renvoie les informations d'un pays au format json
  #
  def send_json_country(self,country):

    # on récupère le pays depuis la base de données
    r = self.db_get_country(country)

    # on n'a pas trouvé le pays demandé
    if r == None:
      self.send_error(404,'Country not found')

    # on renvoie un dictionnaire au format JSON
    else:
      data = {k:r[k] for k in r.keys()}
      json_data = json.dumps(data, indent=4)
      headers = [('Content-Type','application/json')]
      self.send(json_data,headers)


  #
  # Récupération de la liste des pays depuis la base
  #
  def db_get_countries(self,continent=None):
    c = conn.cursor()
    sql = 'SELECT wp, name, capital, latitude, longitude, id, cctld, currency, area, drive_side, calling_code, image FROM countries' 

    # les pays d'un continent
    if continent:
      sql += ' WHERE continent LIKE ?'
      c.execute(sql,('%{}%'.format(continent),))

    # tous les pays de la base
    else :
        c.execute(sql)

    return c.fetchall()


  #
  # Récupération d'un pays dans la base
  #
  def db_get_country(self,country):
    # préparation de la requête SQL
    c = conn.cursor()
    sql = 'SELECT * from countries WHERE wp=?'

    # récupération de l'information (ou pas)
    c.execute(sql,(country,))
    return c.fetchone()


  #
  # On envoie les entêtes et le corps fourni
  #
  def send(self,body,headers=[]):

    # on encode la chaine de caractères à envoyer
    encoded = bytes(body, 'UTF-8')

    self.send_raw(encoded,headers)

  def send_raw(self,data,headers=[]):
    # on envoie la ligne de statut
    self.send_response(200)

    # on envoie les lignes d'entête et la ligne vide
    [self.send_header(*t) for t in headers]
    self.send_header('Content-Length',int(len(data)))
    self.end_headers()

    # on envoie le corps de la réponse
    self.wfile.write(data)

 
#
# Ouverture d'une connexion avec la base de données
#
conn = sqlite3.connect('countries.sqlite')

# Pour accéder au résultat des requêtes sous forme d'un dictionnaire
conn.row_factory = sqlite3.Row

#
# Instanciation et lancement du serveur
#
httpd = socketserver.TCPServer(("", 8080), RequestHandler)
httpd.serve_forever()

