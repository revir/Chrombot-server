# from gevent import monkey
# monkey.patch_all()
from socketio.namespace import BaseNamespace
from flask import Flask, Response, request
from socketio import socketio_manage
from socketio.server import SocketIOServer
# from socketio.mixins import RoomsMixin, BroadcastMixin
from SUtils import logger
from datas import gData
from TaskManager import gMan
from UrlsManager import gUrls
import json,sys

app = Flask(__name__)
reload(sys)
sys.setdefaultencoding('utf-8')

class SuperNamespace(BaseNamespace):
    def recv_connect(self):
        self.emit('connected')
        self.__JSONData = [];

    def on_addFile(self, data):
        data['namespace'] = self
        # logger.info('[temp]'+simplejson.dumps(data))
        gData.downloadQueue.put(data)

    def on_addHtml(self, data):
        print 'on_addHtml: '+data['url']
        gUrls.add(data)

    def on_getHtml(self, data):
        val = gUrls.pop()
        if val:
            data['htmlInfo'] = val
        self.emit('html', data)

    def __writeJSONs(self):
        if(len(self.__JSONData) == 0):
            return
        logger.info('writeJSONs!')

        item = self.__JSONData[0]
        with open(item['expectName'], 'w') as f:
            fileJson = [x['data'] for x in self.__JSONData]
            json.dump(fileJson, f, indent=4, ensure_ascii=False, encoding='utf-8')
            f.flush()
            self.__JSONData = []

    def on_writeJSONs(self, obj):
        logger.debug('on_writeJSONs')
        self.__JSONData.append(obj)
        if(len(self.__JSONData) >= 100):
            self.__writeJSONs()


    def on_taskFinished(self):
        logger.info('taskFinished!');
        self.__writeJSONs()
   

@app.route('/')
def onindex():
    return 'Hello, this is SafeSiteSuper.'

@app.route('/socket.io/<path:rest>')
def socketio(rest):
    try:
        socketio_manage(request.environ, {'/super': SuperNamespace}, request)
    except:
        logger.error('socketio_manage failed!!!')

    return Response()

if __name__ == '__main__':
    try:
        SocketIOServer(('0.0.0.0', 5000), app, namespace="socket.io", policy_server=False).serve_forever()
    except KeyboardInterrupt:
        logger.info('### KeyboardInterrupt...')
        gMan.exit()
        
