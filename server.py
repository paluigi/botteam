import cherrypy
import os
import threading
import sys
import json
import logging
import queue

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
     }
}




class Commands(object):

    def __init__(self):
        self.fifo = queue.Queue()



    exposed = True
    
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def GET(self):
        if self.fifo.empty():
            return {'update':'false','payload':''}
        else:
            payload= self.fifo.get()
            return {'update':'true','payload':payload}
            
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()    
    def POST(self):
        
        input_json = cherrypy.request.json
        self.fifo.put(input_json)
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

if __name__ == '__main__':



    
    cherrypy.tree.mount(Root(), '/',conf)
    cherrypy.tree.mount(
        COMMAND_OBJ, '/api/command',
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