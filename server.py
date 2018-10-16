from construct import *
import json
import sys
import argparse

if sys.version_info >= (3, 0):
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import parse_qs
else:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from urlparse import parse_qs


# This class will handles any incoming request from
# the browser

class myHandler(BaseHTTPRequestHandler):

    # Handler for the GET requests
    def do_GET(self):
        """
        Get query and run auto completion
        :return: display result to json
        """
        path, _, query_string = self.path.partition('?')
        query = parse_qs(query_string)
        if 'prefix' in query.keys() and len(query['prefix']) > 0:
            questions = auto.auto_completion(query['prefix'][0])
            if questions is not None:
                self.wfile.write(json.dumps({"completions": questions}))
            else:
                return
        else:
            return
        return


def create_parser():
    """
    Read in parameters from command line
    :return: parser
    """
    parser = argparse.ArgumentParser(description='Return auto completed questions')
    parser.add_argument('-host', dest='host', default='localhost',
                        help='Host name')
    parser.add_argument('-port', dest='port', default=8000,
                        help='Port number')
    parser.add_argument('-f', dest='fname', default='sample_conversations.json',
                        help='Path to sample conversation file or ngram dictionary json file')
    parser.add_argument('-ngram', dest='ngram', default=5,
                        help='Number of grams used in text analysis')
    parser.add_argument('-n', dest='ncompletion', default=5,
                        help='Number of completed questions returned')
    parser.add_argument('-s', dest='source', default=0,
                        help='Get ngram from sample conversation(0) or from ngram dictionary(1)')
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    PROTOCOL = "http"
    HOST = args.host
    PORT_NUMBER = int(args.port)
    ROUTE_INDEX = "/autocomplete"
    source = int(args.source)
    auto = AutoComplete()
    auto.fname = args.fname
    auto.ngram_n = int(args.ngram)
    auto.num_completion = int(args.ncompletion)

    try:
        # Create a web server and define the handler to manage the
        # incoming request
        if source == 0:
            auto.run_from_sample_conversation()
        elif source == 1:
            auto.run_from_ngram_dict()
        else:
            print ("no such source implemented")
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
