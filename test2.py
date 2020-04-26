#!/usr/bin/env python3
# coding: utf-8

import random
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
import time

from flask import Flask, request, Response
app = Flask(__name__)

def event_stream():
       count = 0
       while True:
           count += 1
           yield 'data: %c (%d)\n\n' % (random.choice('abcde'), count)
           time.sleep(1)


@app.route('/my_event_source')
def sse_request():
       return Response(
               event_stream(),
               mimetype='text/event-stream')


@app.route('/')
def page():
       return '''
<!DOCTYPE html>
<html>
       <head>
           <script type="text/javascript" src="//code.jquery.com/jquery-1.8.0.min.js"></script>
           <script type="text/javascript">
               $(document).ready(
                       function() {
                           sse = new EventSource('/my_event_source');
                           sse.onmessage = function(message) {
                               console.log('A message has arrived!');
                               $('#output').append('<li>'+message.data+'</li>');
                           }

                       })
           </script>
       </head>
       <body>
           <h2>Demo</h2>
           <ul id="output"></ul>
       </body>
</html>
'''


if __name__ == '__main__':
       resource = WSGIResource(reactor, reactor.getThreadPool(), app)
       site = Site(resource)
       reactor.listenTCP(8001, site)
       reactor.run()

