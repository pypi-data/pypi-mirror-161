##    threadsnake. A tiny experimental server-side express-like library.
##    Copyright (C) 2022  Erick Fernando Mora Ramirez
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <https://www.gnu.org/licenses/>.
##
##    mailto:erickfernandomoraramirez@gmail.com

import atexit
import os
import json
from typing import Any, Callable, Dict, List
from base64 import b64decode
from hashlib import md5
from uuid import uuid4
from time import time
from functools import reduce

from threadsnake.tools import PhpServer
from .myhttp.http_classes import Bridge, HttpRequest, HttpResponse, Session, decode_querystring, get_content_type, map_dictionary
from .pypress_classes import Application, Callback, DictProvider, Middleware
from .markdown import create_python_markdown_parser

##Midlewares de nivel global
def session(s:Session) -> Middleware:
    '''Configures session support. Receives an global Session instance'''
    def inner(app: Application, req: HttpRequest, res: HttpResponse, next) -> None:
        app.session = s.create_session(req, res)
        next()
    return inner



def static_files(folder: str) -> Middleware:
    '''Configures static files support. "folder" reffers to the path where files will be search for.'''
    def result(app: Application, req: HttpRequest, res: HttpResponse, next:Callable) -> None:
        fileToSearch = os.sep.join([folder, req.path.replace('\\', '/')])
        #if 'scr' in req.path:
            #print(req.headers)
        if os.path.isfile(fileToSearch):
            contentType = get_content_type(fileToSearch)
            #print(contentType)
            res.read_file(fileToSearch, contentType)
        else:
            next()
    return result

def authorization(app:Application, req:HttpRequest, res:HttpResponse, next) -> None:
    '''
    Configures access control. Decodes authorization parameters. Currently supported: "Bearer Token" 
    and "Basic Authentication".
    '''
    authKey = 'Authorization'
    if authKey in req.headers:
        authType, authValue = req.headers[authKey].split(' ')
        req.authorization[authType] = ''
        if authType == 'Bearer':
            req.authorization[authType] = authValue
        elif authType == 'Basic':
            user, password = b64decode(authValue.encode()).decode().split(':')
            req.authorization[authType] = {'user':user, 'password':password}
        del req.headers[authKey]
    next()

def body_parser(app:Application, req:HttpRequest, res:HttpResponse, next) -> None:
    '''
    Configures "x-www-form-urlencoded" request type support. Loads request parameters sent to the
    params dict of the current HttpRequest instance.
    '''
    if req.contentType != None and 'x-www-form-urlencoded' in req.contentType:
        params = map_dictionary(decode_querystring(req.body.strip()), '&', '=')
        for p in params:
            req.params[p] = params[p]
    next()


def multipart_form_data_parser(tempFilesFolder:str, filesDuration:int=60) -> Middleware:
    '''
    Configures "multipart/form-data" request type support. Loads request parameters sent to the
    params dict of the current HttpRequest instance. Futhermore, if it identifies files uploaded, saves them
    in the "tempFilesFolder" and sets them in the "files" dict of the current HttpRequest instance. Those
    files will be available for at least the number of seconds defined in the "filesDuration" parameter.
    '''
    uploadedFiles = {}
    def inner_function(app:Application, req:HttpRequest, res:HttpResponse, next) -> None:
        def save_bin(path, data):
            with open(path, 'wb') as f:
                f.write(data.encode('latin1'))
        if req.contentType != None and 'multipart/form-data' in req.contentType:
            contentType, boundary = [i.strip() for i in req.contentType.split(';')]
            req.contentType = contentType
            boundary = boundary.strip().replace('boundary=','').replace('"', '')
            boundary = f'--{boundary}'
            body = req.body
            if 'chunked' in req.headers.get('Transfer-Encoding', '') and '\r\n' in body:
                res = ''
                chunk_i = 1
                while chunk_i > 0:
                    split = body.split('\r\n', maxsplit=1)
                    chunk, body = split if len(split) == 2 else [split[0], '']
                    chunk_i = int(chunk, 16)
                    res += body[:chunk_i]
                    body = body[chunk_i+2:]
                body = res
            bodyParameters = [i.strip() for i in body.strip().split(boundary) if len(i.strip()) != 0 and i != '--']
            for param in bodyParameters:
                paramHeader, paramValue = param.split('\r\n\r\n', maxsplit=1)
                paramHeader = paramHeader.replace('\r\n', '; ').replace(': ', '=').replace('"', '')
                paramHeader = dict([tuple(i.split('=', maxsplit=2)) for i in paramHeader.split('; ')])
                if 'filename' in paramHeader:
                    fileName = paramHeader['filename']
                    tempFilePath = os.sep.join([tempFilesFolder, str(uuid4()).replace('-', '')])
                    try:
                        save_bin(tempFilePath, paramValue)
                        req.files[fileName] = {'tempFilePath':tempFilePath}
                        uploadedFiles[tempFilePath] = time() + filesDuration
                        for file in uploadedFiles:
                            if uploadedFiles[file] < time():
                                os.remove(file)
                    except Exception as e:
                        print(str(e))
                elif 'name' in paramHeader and len(paramHeader['name']) > 0:
                    req.params[paramHeader['name']] = paramValue
        next()
    return inner_function

def json_body_parser(app:Application, req:HttpRequest, res:HttpResponse, next) -> None:
    '''
    Configures "json" request type. If identifies a valid json in the request body, it sets
    the dict property of the current HttpRequest instance with the json content.
    '''
    if req.contentType in ['application/json', 'text/json']:
        try:
            req.data = json.loads(req.body.strip())
        except:
            res.status(400).write("Can't decode json body")
    next()

def cors(app: Application, req: HttpRequest, res: HttpResponse, next) -> None:
    '''Configures CORS.'''
    res.headers['Access-Control-Allow-Origin'] = "*"
    next()

def default_headers(headersProvider: DictProvider) -> Middleware:
    '''
    Sets response default headers. Those headers are determined by the result of the function "headersProvider"
    on every request.
    '''
    def child1(app: Application, req: HttpRequest, res: HttpResponse, next) -> None:
        headers = headersProvider()
        for h in headers:
            res.headers[h] = headers[h]
        next()
    return child1

since = time()
requestNumber = 0
def build_default_headers(baseHeaders: Dict[str, Any] = None) -> DictProvider:
    '''
    Provides a standar function for building default headers.
    '''
    def inner() -> Dict[str, Any]:
        global requestNumber
        requestNumber += 1
        headers = baseHeaders or {"Powered-By":"Myself"}
        headers["Server-Epoch-Time"] = str(time())
        headers["Powered-By"] = "Python threadsnake beta"
        headers["Active-Since"] = since
        headers["Request-Count"] = requestNumber
        return headers
    return inner

def identify_client(app: Application, req: HttpRequest, res:HttpResponse, next) -> None:
    '''
    Identifies client printing it in the console.
    '''
    print(f'connection from {req.clientAddress}')
    next()

def header_inspector(headerName: str, action: Callable) -> Middleware:
    '''
    Calls "action" every time the header "headerName" is identified in a request.
    '''
    def result(app: Application, req: HttpRequest, res: HttpResponse, next)  -> None:
        if headerName in req.headers:
            action(req.headers[headerName])
        next()
    return result

def validates_request(predicate:Callable[[HttpRequest], bool], onFailMessage:str = None, onFailStatus:int = 400) -> Callable[[Callback], Callback]:
    '''
    Generalizes request validation using a "predicate" function wich receives the current HttpRequestInstance
    and returns a boolean. If the result is false, the client receives an "onFailStatus" status code and an
    "onFailMessage" message. Otherwise the pipeline executes normally.
    '''
    def child1(middleware:Callback) -> Callback:
        def child2(app:Application, req:HttpRequest, res: HttpResponse) -> None:
            if predicate(req):
                middleware(app, req, res)
            else:
                res.end(onFailMessage or "Bad Request", onFailStatus)
        return child2
    return child1

def accepts(contentTypes:List[str]) -> Callable[[Callback], Callback]:
    '''
    Validates the HttpRequest content-type against the list of "contentTypes", with are the allowed ones. 
    Returns an UnsuportedMediaType status code if the content-type is not in the list. Otherwise the 
    pipeline executes normally. Delegates to "validates_request".
    '''
    def child1(middleware:Callback) -> Callback:
        return validates_request(lambda r: r.contentType in contentTypes, onFailStatus=415)(middleware)
    return child1

def requires_json(middleware:Callback) -> Callback:
    '''Especialization of accepts wich just allows json requests.'''
    return accepts(['application/json', 'text/json'])(middleware)


def time_measure(app:Application, req:HttpRequest, res:HttpResponse, next) -> None:
    '''
    Ideally measures the time than all pipeline takes to execute.
    '''
    startTime = time()
    next()
    interval = (time() - startTime) * 1000
    res.headers['process-time-ms'] = str(interval)
    #print(f"Request from {req.clientAddress} processed in {interval} milliseconds")


def validates_header(headerName:str, callback:Callable, notSuchHeaderStatus = 400, message:str=None) -> Callable[[],Callback]:
    '''
    Validates if "headerName" is present in the request and matches a "callback".
    '''
    def child1(middleware:Callback) -> Callback:
        def child2(app:Application, req:HttpRequest, res:HttpResponse) -> None:
            if headerName in req.headers and callback(req.headers[headerName]):
                middleware(app, req, res)
            else:
                res.end(message or f"Missing or Invalid header value: {headerName}", notSuchHeaderStatus)
        return child2
    return child1


def requires_parameters(params:List[str]) -> Callable[[Callback], Callback]:
    '''
    Enforces the presence "params" int the request.
    '''
    def inner(funct:Callback) -> Callback:
        def mutated(self:Application, req:HttpRequest, res:HttpResponse) -> None:
            missingParameters = [i for i in params if i not in [p for p in req.params]]
            if len(missingParameters) > 0:
                res.end('Missing parameters: ' + reduce(lambda a, b: f"{a}, {b}", missingParameters), 400)
            else:
                funct(self, req, res)
        return mutated
    return inner


def logs_execution(middleware:Callback) -> Callback:
    '''Marks an endpoint to print every time it gets called.'''
    def inner(app:Application, req:HttpRequest, res:HttpResponse) -> None:
        print(f':::{req.method} {req.url} -> {middleware.__qualname__}')
        middleware(app, req, res)
    return inner


cache = {}
def uses_cache(cacheSize:int) -> Callable[[Callback], Callback]:
    '''Marks a endpoint to response to be cached by the server.'''
    def decorator(middleware: Callback):
        def inner(app:Application, req:HttpRequest, res:HttpResponse) -> None:
            if 'Cache-Control' in req.headers and req.headers['Cache-Control'] == 'no-cache':
                middleware(app, req, res)
                return
            reqHash = md5(req.raw.encode()).hexdigest()
            if reqHash in cache:
                res.cache(cache[reqHash])
            else:
                middleware(app, req, res)
                while len(cache) > cacheSize and cacheSize > 0:
                    del cache[list(cache.keys())[0]]
                cache[reqHash] = str(res)
        return inner
    return decorator


def uses_php(path:str, pointsTo:str, port:int, hostName:str='localhost', phpPath:str='php') -> Middleware:
    '''Uses php to serve files in "path". Available only on windows.'''
    srv = PhpServer(pointsTo, port, hostName, phpPath).start()
    atexit.register(lambda: srv.stop())
    print(f'PHP server hosted at {hostName}:{port}')
    def inner(app:Application, req:HttpRequest, res:HttpResponse, next) -> None:
        if req.url.startswith(path):
            data = Bridge(port, hostName).send(req.raw)
            res.cache(data)
        next()
    return inner

def pico_swagger(app:Application, req:HttpRequest, res:HttpResponse) -> None:
    '''Minimal implementation of a middleware wich prints every endpoint registered.'''
    swaggerSylesParameter = "stylesheet"
    endpointParameter = 'endpoint'
    if swaggerSylesParameter in req.params and req.params[swaggerSylesParameter] == '1':
        styleSheet = \
        '.sw-h1{font-size:1.7em;padding:0.2em;}'\
        '.sw-h2{font-size:1.3em;padding:0.1em 1em;}'\
        '.sw-h3{padding:0.1em 3em;}'
        res.end(styleSheet).content_type('text/css')
        return
    elif(endpointParameter in req.params):
        res.write('I promise to someday give you a real swagger for this : ')
        res.end(req.params[endpointParameter])
        return
    
    def link(url:str, text:str = None):
        baseUrl = req.baseUrl
        text = text or url
        return f'<a href="{baseUrl}?{endpointParameter}={url}">{text}</a>'
    
    def tag(text:str, name:str='div', attrs:Dict[str, str] = None):
        res = f"<{name}"
        if attrs != None:
            res += reduce(lambda a,b: f'{a}{b}', [f' {i}="{attrs[i]}"' for i in attrs])
            pass
        res += f">{text}</{name}>"
        return res
    
    res.write(tag(tag("", "link", {"rel":"stylesheet", "href":f"{req.baseUrl}?{swaggerSylesParameter}=1"}), "head"))
    html = tag("pico-Swagger", "div", {"class":"sw-h1"})
    for i in app.routes:
        html += tag(i, "div", {"class":"sw-h2"})
        for r in app.routes[i]:
            if r == req.baseUrl:
                continue
            html += tag(link(r), "div", {"class":"sw-h3"})
            funct = app.routes[i][r]
    res.end(tag(html, "body", {"class":"sw-panel"})).content_type('text/html')

def serve_static_markdown(base:str = 'markdown', extension:str = '.md', maxCached:int = 10, encoding:str = 'latin1') -> Middleware:
    '''Allows serving markdown files statically as html. Partially supported.'''
    markdownCache = {}
    markdownKeys = []
    parser = create_python_markdown_parser()
    def serve_markdown(app:Application, req:HttpRequest, res:HttpResponse, next):
        path = (req.path if not req.path.startswith('/') else req.path[1:]).replace('/', os.sep)
        path = os.sep.join([base, path]) + extension
        if os.path.exists(path) and os.path.isfile(path):
            data = ''
            with open(path, 'r', encoding=encoding) as r:
                data = r.read()
            hash = md5(data.encode(encoding)).hexdigest()
            if hash in markdownCache:
                data = markdownCache[hash]
            else:
                data, style = parser.parse_str(data)
                data = f'''
                    <html>
                        <head>
                            <style>{style}</style>
                        </head>
                        <body>
                            {data}
                        </body>
                    </html>
                '''
                markdownCache[hash] = data
                markdownKeys.insert(0, hash)
                while len(markdownKeys) > maxCached:
                    del markdownCache[markdownKeys.pop()]
            res.status(200).html(data)
        else:
            next()
    return serve_markdown