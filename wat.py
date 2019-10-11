import ibm_watson 
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json
import requests
import textwrap
import random
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

aut_key = "---TMDB API KEY HERE---";
url = "https://api.themoviedb.org/3/genre/movie/list?"
params = {'api_key' : aut_key, 'language' : 'pt-BR'}

response = requests.get(url, params).json()

genre_to_id = dict()
for d in response['genres']:
  if d['name'] == 'Ficção científica':
    d['name'] = 'Ficção'
  genre_to_id[d['name']] = d['id']

#conecting with watson
authenticator = IAMAuthenticator('---WATSON API KEY HERE---')
url = 'https://gateway.watsonplatform.net/assistant/api'
assistant = ibm_watson.AssistantV2(
  authenticator=authenticator,
  version='2019-02-28'
)

assistant.set_service_url(url)
assistant_id = '9d86417c-dc7f-4333-bd6a-2989a13e783f'

response = assistant.create_session(
    assistant_id=assistant_id
).get_result()
print(response)
session_id = response['session_id']

flag = int(0)
#

#prints a list of movies to the user
#if overview is true, then the overview of each moive will be printed as well
def print_movies(movie_list, overview = True):
  ans = ''
  ans += str('Encontramos %d ótimos filmes para lhe recomendar!\n' %(len(movie_list)))
  cnt = 1
  #wrapper = textwrap.TextWrapper(width = 80)
  for movie in movie_list:
    print('\n\n--------------------------------------')
    print('%d : %s' %(cnt, movie['Nome']))
    #print('Data de lançamento : %s\n\n' %movie['Data'])
    
    ans += str('\n\n--------------------------------------\n')
    ans += str('%d : %s\n' %(cnt, movie['Nome']))
    if (movie['Data']):
      ans += str('Data de lançamento : %s\n\n' %movie['Data'])
    
    if overview == True and movie['Sinopse']:
      ans += str('Sinopse : %s' %movie['Sinopse'])
      
    cnt += 1
  return ans

def parse_movies(results, include_popularity = True):
    ans = list()
    for d in results:
        clean_dict = dict()
        clean_dict['Nome'] = d['title']
        clean_dict['ID'] = d['id']
        if 'popularity' in d:
            clean_dict['Popularidade'] = d['popularity']
        else:
            clean_dict['Popularidade'] = 0
        if 'overview' in d:
            clean_dict['Sinopse'] = d['overview']
        if 'release_date' in d:
            clean_dict['Data'] = d['release_date']
        ans.append(clean_dict)
    return ans

def parse_actors(results):
  ans = list()
  for d in results:
    clean_dict = dict()
    clean_dict['Nome'] = d['name']
    clean_dict['Popularidade'] = d['popularity']
    clean_dict['ID'] = d['id']
    clean_dict['Filmes'] = d['known_for']
    ans.append(clean_dict)
  return ans

#returns a list with the 5 top rated movies in the specified genres
#each movie is a python dict with the keys 'Nome', 'Sinopse' and 'Data'
def discover_by_genders(genre_list):
  discover_url = "https://api.themoviedb.org/3/discover/movie?"

  genre_qry = ''
  for genre in genre_list:
    genre_qry += str(genre_to_id[genre]) + ','

  genre_qry = genre_qry[:-1]

  discover_params = {'api_key' : aut_key, 'language' : 'pt-BR', 'sort_by' : 'popularity.desc', 'page' : 1,
            'include_adult' : False, 'include_video' : False, 'with_genres' : genre_qry}

  r = requests.get(discover_url, discover_params).json()
  ans = parse_movies(r['results'])
  random.shuffle(ans)
  ans = ans[:5]
  return ans


def discover_by_person(person):
  person = person.lower().replace(' ', '+')
  person_url = 'https://api.themoviedb.org/3/search/person?'
  params = {'api_key' : aut_key, 'language' : 'pt-BR', 'query' : person}
  r = requests.get(person_url, params).json()
  
  if (r['total_results'] == 0):
    return 'Nao encontrei nada :('
    
  ans = parse_actors(r['results'])
  ans = sorted(ans, key = lambda x : x['Popularidade'], reverse = True)[0]
  movies = parse_movies(ans['Filmes'], include_popularity = False)
  return movies

def get_popular_movies():
  popular_url = 'https://api.themoviedb.org/3/movie/popular?'
  params = {'api_key' : aut_key, 'language' : 'pt-BR'}
  r = requests.get(popular_url, params).json()
  ans = parse_movies(r['results'])
  random.shuffle(ans)
  ans = ans[:5]
  return ans

def get_recommendations(movie):  
  movie = movie.lower().replace(' ', '+')

  search_url = 'https://api.themoviedb.org/3/search/movie?'
  params = {'api_key' : aut_key, 'language' : 'pt-BR', 'query' : movie}
  
  r = requests.get(search_url, params).json()
  
  if (r['total_results'] == 0):
    return 'Nao encontrei nada :('
  
  candidates = parse_movies(r['results'])

  candidates = sorted(candidates, key = lambda x : x['Popularidade'], reverse = True)

  rec_url = 'https://api.themoviedb.org/3/movie/{movie_id}/recommendations?'
  rec_url = rec_url.replace('{movie_id}', str(candidates[0]['ID']))
  params = {'api_key' : aut_key, 'language' : 'pt-BR'}

  r = requests.get(rec_url, params).json()
  ans_final = parse_movies(r['results'])
  
  ans_final = ans_final[:min(5, len(ans_final))]
  return ans_final

def parse(text):
  if text == None:
    return None
  return {'message_type':'text', 'text':text}
  
def sendWatson(message):
  if (flag != 0):
    return flag, message
  
  response = assistant.message(
      assistant_id=assistant_id,
      session_id=session_id,
      input=parse(message)
  ).get_result()
  return flag, response
  
def updateFlag(x):
  global flag
  flag = int(x)

def start(update, context):
  bem_vindo = sendWatson(None)[1]
  bem_vindo = bem_vindo['output']['generic'][0]['text']
  print(bem_vindo)
  context.bot.send_message(chat_id=update.effective_chat.id, text=bem_vindo)

def handler(update, context):
  mens_client = update.message.text
  print('Recebi: %s\n' %mens_client)
  #print('flag é %d\n' %flag)
  ans = 'Sem resposta'
  
  flag_cur, response = sendWatson(mens_client)

  if (flag_cur == 1):
    ans = get_recommendations(response)
    if (type(ans) != str):
      ans = print_movies(ans)
    updateFlag(0)
  elif (flag_cur == 2):
    ans = discover_by_person(response)
    if (type(ans) != str):
      ans = print_movies(ans)
    updateFlag(0)
  else:
    print(response)
    if (response['output']['intents'] and response['output']['intents'][0]['intent'] == 'Gênero'):
      gens = []
      for x in response['output']['entities']:
        gens.append(x['entity'])
      print(gens)
      ans = print_movies(discover_by_genders(gens))
    elif (response['output']['intents'] and response['output']['intents'][0]['intent'] == 'Populares_do_momento'):
      ans = print_movies(get_popular_movies())
    elif (response['output']['intents'] and response['output']['intents'][0]['intent'] == 'Filmes_similares'):
      ans = 'Qual o nome do seu filme preferido ?'
      updateFlag(1)
    elif (response['output']['intents'] and response['output']['intents'][0]['intent'] == 'Pessoa'):
      ans = 'Qual o nome do seu ator/diretor preferido ?'
      updateFlag(2)
    else:
      ans = response['output']['generic'][0]['text']

  context.bot.send_message(chat_id=update.effective_chat.id, text=ans)

def main():
  
  updater = Updater(token='---TELEGRAM API KEY---', use_context=True)    
  dispatcher = updater.dispatcher
  start_handler = CommandHandler('start', start)
  mens_handler = MessageHandler(Filters.text, handler)
  dispatcher.add_handler(start_handler)
  dispatcher.add_handler(mens_handler)
  updater.start_polling()

if __name__ == '__main__':
  main()