
import networkx as nx
import matplotlib.pyplot as plt
import time
import requests
from operator import itemgetter
import json


def lastfm_request(api_method,artist='',track=''):
    ''' 
        Pega os dados a partir da API last fm
        0 = tags de uma musica
        1 = pesquisar por uma musica
        2 = top 30 musicas mais ouvidas no brasil
    '''

    if api_method==0:
        method = f"track.gettoptags&artist={artist}&track={track}"
    elif api_method==1:
        method = f"track.search&track={track}&limit=1"
    else:
        method = "geo.gettoptracks&country=Brazil&limit=30"
    
    key ="3dc1e72157f70010ef87db6b769fbfe7"
    API_URL = f'http://ws.audioscrobbler.com/2.0/?method={method}&api_key={key}&format=json'
    return requests.request(method='get', url=API_URL).json()

def predecessor(G, start):
    '''
        Recebe o grafo e o nó inicial
        Retorna uma  dict de "pais" pra cada nó
    '''

    if start not in G:
        raise False

    level = 0  
    nextlevel = [start]  
    explored = {start: level}  
    pred = {start: []}  
    while nextlevel:
        level = level + 1
        thislevel = nextlevel
        nextlevel = []
        for v in thislevel:
            for w in G[v]:
                if w not in explored:
                    pred[w] = [v]
                    explored[w] = level
                    nextlevel.append(w)
                elif explored[w] == level:  
                    pred[w].append(v)  

    return pred

def find_paths(start, target, pred):
    '''
        Recebe um nó inicial, um nó final e um dicionario contendo os pais de cada nó
        Gera um objeto com todos os menores caminhos entre o nó inicial e o nó final
    '''

    if target not in pred or {target}==start:
        return None

    explored = {target}
    stack = [[target, 0]]
    top = 0
    while top >= 0:
        node, i = stack[top]
        if node in start:
            yield [p for p, n in reversed(stack[: top + 1])]
        if len(pred[node]) > i:
            stack[top][1] = i + 1
            next = pred[node][i]
            if next in explored:
                continue
            else:
                explored.add(next)
            top += 1
            if top == len(stack):
                stack.append([next, 0])
            else:
                stack[top][:] = [next, 0]
        else:
            explored.discard(node)
            top -= 1



def recommend(song):
 
    #construindo o grafo a partir da api
    top_tracks = lastfm_request(2)['tracks']['track']
    songs_graph = {}
    songs_list = []
    tags_list = []
    song_links = {}
    for track in top_tracks:
        tags = lastfm_request(0,track["artist"]["name"],track["name"])['toptags']['tag'][:3]
        if track["name"] not in songs_graph:
            songs_list.append(track["name"])
            songs_graph[track["name"]] = []
            song_links[track["name"]] = track["url"]
            for tag in tags:
                songs_graph[track["name"]].append(tag["name"])
                if tag["name"] not in songs_graph:
                    tags_list.append(tag["name"])
                    songs_graph[tag["name"]] = [track["name"]]
                else:
                    songs_graph[tag["name"]].append(track["name"])
    
    #tenta encontrar a música que o usuário digitou
    result = lastfm_request(1,track=song)
    
    #retorna falso se a música não foi encontrada
    if result['results']['trackmatches']['track'] == []:
        
        return False
    
    #resultado encontrado
    result = result['results']['trackmatches']['track'][0]

    #pega as 3 tags mais populares para a musica
    tags = lastfm_request(0,result['artist'],result['name'])['toptags']['tag'][:3]
    
    #adiciona a musica e as tags ao grafo
    if result['name'] not in songs_graph:
            songs_graph[result['name']] = []
            songs_list.append(result['name'])
            for tag in tags:
                songs_graph[result["name"]].append(tag["name"])
                if tag["name"] not in songs_graph:
                    tags_list.append(tag["name"])
                    songs_graph[tag["name"]] = [result["name"]]
                else:
                    songs_graph[tag["name"]].append(result["name"])


    best_matches = []
    
    #calcula as musicas com o caminho mais curto até a música digitada pelo usuário
    for node in songs_list:
        parentage = predecessor(songs_graph, node)
        paths = list(find_paths({node}, result['name'], parentage))
        if paths != []:
            num_paths = len(paths)
            path_lenght = len(paths[0])
            if path_lenght <=5: # não consideramos músicas muito distantes 
                best_matches.append({'name':node,'lenght':path_lenght,'number':num_paths})
                

    return [sorted(best_matches, key=lambda k: (k['lenght'], -k['number'])), f"{result['name']} de {result['artist']}", song_links]