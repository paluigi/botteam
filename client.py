#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests
import json
import pprint
import time
import random
import threading

pp = pprint.PrettyPrinter(indent=4)

PORTAL_URL = 'http://botteam.eu.ngrok.io/api/command'

'''
def get_webcams():
    seed = random.randint(0, 10)
    link = f"https://tourism.opendatahub.bz.it/v1/WebcamInfo?pagenumber=1&pagesize=3&active=true&odhactive=true&seed={seed}&removenullvalues=false"
    results_json = requests.get(link)
    results = json.loads(results_json.text)
    webcams = results.get("Items")
    image_urls = [item.get("Webcamurl") for item in webcams]
    shortnames = [item.get("Shortname") for item in webcams]
    trivia = [{"key": i, "url": url, "name": name} for (i, url, name) in zip([1, 2, 3], image_urls, shortnames)]
    return trivia
'''


def domanda(trivia,text):
    command = {}
    command["comando"]="domanda"
    command["domanda"]={}
    command["domanda"]["testo"]=text
    command["domanda"]["immagini"]=list(map(lambda i: i["url"],trivia))

    send(command)


def answer(text, correct, image):
    risposta = {}
    risposta["comando"]="risposta"
    risposta["risposta"]={}
    risposta["risposta"]["testo"]=text
    risposta["risposta"]["risposta_esatta"]=correct
    risposta["risposta"]["immagine"]=image
    risposta["risposta"]["eventi"]=[]
    
    send(risposta)

def send(c):
    r = requests.post(PORTAL_URL, json = c)
    pp.pprint(r.status_code)
    
    #time.sleep(7)


def main():
    
    
    
    
    trivia = get_webcams()
    
    choice = random.randint(0, 2)
    
    command = {}
    command["comando"]="domanda"
    command["domanda"]={}
    command["domanda"]["testo"]="Quale delle tre è " + trivia[choice]["name"]+" ?"
    
    command["domanda"]["immagini"]=list(map(lambda i: i["url"],trivia))

    send(command)
    
    risposta = {}
    risposta["comando"]="risposta"
    risposta["risposta"]={}
    risposta["risposta"]["testo"]="La riposta giusta è "+ str(choice+1)
    risposta["risposta"]["risposta_esatta"]="true"
    risposta["risposta"]["immagine"]=trivia[choice]["url"]
    risposta["risposta"]["eventi"]=[]
    
    send(risposta)
    
    

    
    classifica = {}
    classifica["comando"]="classifica"
    classifica["classifica"] = []
    
    usernames = ["paluigi","daniele","test","livebot","boh"]
    andamento = ["up","down"]
    
    for i in range(0,5):
        user = {}
        user["username"]  = usernames[random.randint(0, 4)]
        user["punteggio"] = random.randint(1, 3)
        user["andamento"] = andamento[random.randint(0, 1)]
        classifica["classifica"].append(user)
    send(classifica)
    
    
    reset = {}
    reset["comando"]="reset"
    
    send(reset)

if __name__ == '__main__':

    
    def mainloop():
        while True:
            main()
    
    x = threading.Thread(target=mainloop, args=())
    x.start()
    x.join()
    