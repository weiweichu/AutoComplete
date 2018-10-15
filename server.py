from construct import *
import json
import sys

if sys.version_info >= (3, 0):
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import parse_qs
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from urlparse import parse_qs

PROTOCOL = "http"
HOST = "localhost"
PORT_NUMBER = 8000
ROUTE_INDEX = "/autocomplete"
auto = AutoComplete()


# This class will handles any incoming request from
# the browser

class myHandler(BaseHTTPRequestHandler):

    def info(self):
        """
        index.html
        :return:
        """
        self.wfile.write('<html>')
        self.wfile.write('<head>')
        self.wfile.write('    <meta charset="UTF-8">')
        self.wfile.write('    <title>AutoCompletion</title>')
        self.wfile.write('</head>')
        self.wfile.write('<body>')
        self.wfile.write('    <form id="input" method="GET" action="">')
        self.wfile.write('        Question prefix: <input type = "text" name = "prefix" />')
        self.wfile.write('    </form>')
        self.wfile.write('</body>')
        self.wfile.write('</html>')

    # Handler for the GET requests
    def do_GET(self):
        """
        Get query and run auto completion
        :return: display result to json
        """
        path, _, query_string = self.path.partition('?')
        query = parse_qs(query_string)
        if path == ROUTE_INDEX:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.info()
            if 'prefix' in query.keys() and len(query['prefix']) > 0:
                questions = auto.auto_completion(query['prefix'][0])
                if questions is None:
                    return
                else:
                    self.wfile.write(json.dumps({"completion": questions}))
        else:
            return
        return


try:
    # Create a web server and define the handler to manage the
    # incoming request

    auto.run()
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print("Starting server, use <Ctrl-C> to stop...")
    print(u"Open {0}://{1}:{2}{3} in a web browser.".format(PROTOCOL,
                                                            HOST,
                                                            PORT_NUMBER,
                                                            ROUTE_INDEX))

    # Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
