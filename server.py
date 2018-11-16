# -*- coding: utf-8 -*-

"""Http server for handle api with post method"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import preprocessor
import summarization
from urllib import parse

filename = '법별 집행기준(법명,조명,id,조내용)_20180427'
keywords = ['상속세', '증여세']


def data_proprecess(keywords):

    preprocessed_data = preprocessor.preprocess(filename)
    data2sen = preprocessor.data2sentence(preprocessed_data)
    matched_data = preprocessor.keyword_matching(data2sen, keywords)
    preprocessor.data2file(matched_data, filename)


def summary(topN, window, coef, threshold):
    tr = summarization.TextRank(window=window, coef=coef, threshold=threshold)
    print('Load...')
    tr.loadSents(summarization.RawSentenceReader(filename + '_matched_Data.txt'))
    print('Build...')
    tr.build()
    ranks = tr.rank()
    message = ''
    for k in sorted(ranks, key=ranks.get, reverse=True)[:topN]:
        print("\t".join([str(k), str(ranks[k]), str(tr.dictCount[k])]))
        message += str(tr.dictCount[k]) + '<br><br>'

    return message

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ThreadedHTTPServer handle requests with threads"""
    pass

class SummarizerServerHandler(BaseHTTPRequestHandler): # Handle http request
    """Summarizer server"""
    def _chk_req_type(self, req_type, args):
        pass

    def do_GET(self):
        """Handle get requests"""

        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html; charset=UTF-8')
        self.end_headers()

        topN, window, coef, threshold = 20, 5, 1.0, 0.001
        keywords = []

        request_uri = self.path[1:]

        if request_uri == 'favicon.ico':
            pass
        elif request_uri != '':
            parameter = request_uri.split(',')
            keywords = parameter[4:]
            for i in range(len(keywords)):
                keywords[i] = parse.unquote(keywords[i])
            topN, window, coef, threshold = int(parameter[0]), int(parameter[1]), float(parameter[2]), float(parameter[3])


        # Send summary message back to client
        data_proprecess(keywords)
        message = summary(topN, window, coef, threshold)

        # Write content as utf-8 data
        self.wfile.write(bytes(message, 'utf-8'))
        # self.wfile.write(bytes('클라이언트가 요청한 경로: ', 'utf-8'))
        # self.wfile.write(bytes(self.path, 'utf-8'))

    def do_POST(self):
        """Handle post requests"""

        # Read request uri
        request_uri = self.path[1:]

        # Read request parameters
        content_length = int(self.headers['Content-Length'])
        params = self.rfile.read(content_length)
        params = params.decode('utf-8')
        fields = dict(parse.parse_qsl(params))

        topN, window, coef, threshold = 20, 5, 1.0, 0.001 # default
        keywords = []

        for param in fields.keys():
            if param == 'topN':
                topN = int(fields[param])
            elif param == 'window':
                window = int(fields[param])
            elif param == 'coef':
                coef = float(fields[param])
            elif param == 'threshold':
                threshold = float(fields[param])
            elif param == 'keyword1' or param == 'keyword2':
                keywords.append(parse.unquote(fields[param]))
            else:
                pass

        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html; charset=UTF-8')
        self.end_headers()

        # Send summary message back to client
        data_proprecess(keywords)
        message = summary(topN, window, coef, threshold)

        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))


if __name__ == '__main__':
    try:
        # TODO (tsoopark): connect with configuration # 211.39.140.245 # port : 8095
        summary_server = ThreadedHTTPServer(('localhost', 8080), SummarizerServerHandler) # 이렇게 하면 localhost에서 오는 요청만 받는거다....!
        summary_server.serve_forever() # Wait request
    except KeyboardInterrupt as e:
        pass



# function post_to_url(path, params, method) {
#     method = method || "post"; // Set method to post by default, if not specified.
#     // The rest of this code assumes you are not using a library.
#     // It can be made less wordy if you use one.
#     var form = document.createElement("form");
#     form.setAttribute("method", method);
#     form.setAttribute("action", path);
#     for(var key in params) {
#         var hiddenField = document.createElement("input");
#         hiddenField.setAttribute("type", "hidden");
#         hiddenField.setAttribute("name", key);
#         hiddenField.setAttribute("value", encodeURIComponent(params[key]));
#         form.appendChild(hiddenField);
#     }
#     document.body.appendChild(form);
#     form.submit();
# }
#
# post_to_url('http://210.39.140.245:8095/', {'topN':10,'window':7,'coef':0.8,threshold:0.002,keyword1:'상속세',keyword2:'증여세'});