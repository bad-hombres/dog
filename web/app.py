from tornado import websocket, web, ioloop, gen
import json
import zmq
import os
import sqlite3

cl = []

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)

    def on_close(self):
        if self in cl:
            cl.remove(self)

class ApiHandler(web.RequestHandler):
    base_dir = os.path.join(os.environ["HOME"], ".dog")

    @web.asynchronous
    def get(self, *args):
        id = self.get_argument("id")
        if id == "projects":
            dirs = os.listdir(ApiHandler.base_dir)
            self.write({"response": dirs})

        if id == "tables":
            project = self.get_argument("project")
            db = sqlite3.connect(os.path.join(ApiHandler.base_dir, project, "project.db"))                                                
            c = db.cursor()                                                                                            
            response = {"response": []}                                                                                                                       
            try:                                                                                                       
                c.execute("SELECT name FROM sqlite_master WHERE type='table'")                
                for row in c.fetchall():
                    response["response"].append(row[0])
                                                                                                                       
            except Exception as ex:                                                                                    
                print ex                                                                                               
            finally:                                                                                                   
                c.close()                                                                                              
                db.commit()                                                                                            
                db.close()                                                                    
            self.write(response)

        if id == "contents":
            project = self.get_argument("project")
            table = self.get_argument("table")
            response = {"response": []}                                                                                                                       
            if table == "files":
                files = os.listdir(os.path.join(ApiHandler.base_dir, project))
                response["response"] = map(lambda x: "<a href='/files/%s/%s'>%s</a>" % (project, x, x), files)
            else:
                db = sqlite3.connect(os.path.join(ApiHandler.base_dir, project, "project.db"))                                                
                c = db.cursor()                                                                                            
                try:                                                                                                       
                    c.execute("SELECT * FROM %s" % table)
                    for row in c.fetchall():
                        response["response"].append(row[0])
                                                                                                                           
                except Exception as ex:                                                                                    
                    print ex                                                                                               
                finally:                                                                                                   
                    c.close()                                                                                              
                    db.commit()                                                                                            
                    db.close()                                                                    
            self.write(response)

        self.finish()

    @web.asynchronous
    def post(self):
        pass

app = web.Application([
    (r'/', IndexHandler),
    (r'/api', ApiHandler),
    (r'/ws', SocketHandler),
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
    (r'/files/(.*)', web.StaticFileHandler, {'path': ApiHandler.base_dir}),
])

context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5556")
subscriber.setsockopt(zmq.SUBSCRIBE, b'LOG')

poller = zmq.Poller()
poller.register(subscriber, zmq.POLLIN)

@gen.engine
def get_message():
    try:
        socks = dict(poller.poll(10))
        if subscriber in socks and socks[subscriber] == zmq.POLLIN:
            content = subscriber.recv_multipart()
            for c in cl:                
                c.write_message(str(content[1]))
    finally:
        ioloop.IOLoop.instance().add_callback(get_message)
    

if __name__ == '__main__':
    app.listen(8888)
    ioloop.IOLoop.instance().add_callback(get_message)
    ioloop.IOLoop.instance().start()
