import cherrypy
import os
import threading
import sys
import json
import logging
import queue
import random
import requests

'''
cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 18881,
                        'server.ssl_module': 'builtin',
                        'server.ssl_certificate': 'cert.pem',
                        'server.ssl_private_key': 'privkey.pem',
                       })
'''

cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 18881,
                       })




class Root(object): pass

class AlpiServer:
    @cherrypy.expose
    def index(self):
        return "Hello friend!!!"
    index_shtml = index_html = index_htm = index_php = index

location = os.path.join(os.path.dirname(os.path.realpath(__file__)), '')

conf = {
     '/': {
         'tools.staticdir.on': True,
         'tools.staticdir.dir': '',
         'tools.staticdir.root': location,
         'tools.staticdir.index': 'index.html',
         'tools.caching.on' : False,
     }
}




class Commands(object):
    
    fifo = queue.Queue()
    
    exposed = True
    
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def GET(self):
        if Commands.fifo.empty():
            return {'update':'false','payload':''}
        else:
            payload= Commands.fifo.get()
            return {'update':'true','payload':payload}
            
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()    
    def POST(self):
        
        input_json = cherrypy.request.json
        Commands.fifo.put(input_json)
        return {'ack':'ok','command':input_json["comando"]}
    
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()    
    def PUT(self, id, title=None, artist=None):
        return {'error':'not yet implemented'}
    
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()    
    def DELETE(self, id):
        return {'error':'not yet implemented'}
    

        
COMMAND_OBJ = Commands()

class RandomImage(object):

     exposed = True
     
     def GET(self):
        seed = random.randint(0, 10)
        link = f"https://tourism.opendatahub.bz.it/v1/WebcamInfo?pagenumber=1&pagesize=1&active=true&odhactive=true&seed={seed}&removenullvalues=false"
        results_json = requests.get(link)
        results = json.loads(results_json.text)
        webcams = results.get("Items")
        image_urls = [item.get("Webcamurl") for item in webcams][0]
        return image_urls


RANDIMAGE_OBJ = RandomImage()



if __name__ == '__main__':



    
    cherrypy.tree.mount(Root(), '/',conf)
    cherrypy.tree.mount(
        COMMAND_OBJ, '/api/command',
        {'/':
            {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
        }
    )
    cherrypy.tree.mount(
        RANDIMAGE_OBJ, '/api/randimage',
        {'/':
            {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
        }
    )
    '''
    cherrypy.tree.mount(
        LINK_OBJ, '/show',
        {'/':
            {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}
        }
    )
    

    '''
    
   
    
    
    cherrypy.engine.start()
    cherrypy.engine.block()