from twisted.web import server, resource, static
from twisted.internet import reactor
import os.path
import re 

class site (resource.Resource):
    isLeaf = True 
    content_type = None
    directory= None
    extension= None
    def getChild (self, name, request):
        if name == '':
            return self
        else :
            return resource.Resource.getChild(self,name,request)
    def render_GET (self, request):
        #request.setHeader ("Content-Type","text/html; charset =utf-8")
        #return "<html> hello world </html>".encode('utf-8')
        file = request.path.decode('ascii')
        #return "file value is %r"%(file)
        if ".." in file:
            request.setResponseCode(400)
            return ""
        if not os.path.isfile(file):
            request.setResponseCode(404)
            return ""
        with open(file) as source:
            return source.read()

#root= static.File ("/home/hardi/Downloads/awesomefile.txt") easier approach
httpserver = server.Site (site())
reactor.listenTCP (8080, httpserver)
reactor.run()
'''
Usage : enter localhost:8080/home/user10702/Downloads/filename 
Output : returns the file 
'''