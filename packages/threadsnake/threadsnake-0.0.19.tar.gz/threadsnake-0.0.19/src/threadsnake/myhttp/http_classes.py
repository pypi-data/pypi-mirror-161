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

from functools import reduce
import json
from pydoc import cli
import re
import socket
from threading import Thread
import random
import time
from turtle import color
from typing import Any
import uuid
import os
from enum import IntEnum
from .logging import *

class RedirectType(IntEnum):
    MOVED_PERMANENT = 301
    PERMANENT_REDIRECT = 308
    FOUND = 302
    SEE_OTHER = 303
    TEMPORARY_REDIRECT = 307
    MULTIPLE_CHOICE = 301
    NOT_MODIFIED = 304

def get_absolute_path(fileName):
    return os.sep.join([os.sep.join(__file__.split(os.sep)[:-1]), fileName])

responseCodes = {}
threadsnakeIcon = ''

with open(get_absolute_path('response_codes.txt'), 'r') as f:
    for l in [i.strip() for i in f.readlines()]:
        values = l.split('\t')
        if len(values) > 1:
            responseCodes[int(values[0])] = values[1]
        else:
            print(f'Invalid line on response_codes.txt: {values}')

with open(get_absolute_path('icon.txt'), 'rb') as f:
    threadsnakeIcon = f.read().decode('latin1')


contentTypes = {
    "text/": ["html", "css"],
    "text/javascript": ["js"],
    "text/html": ["htm"],
    "application/": ["json", "xml", "pdf", "exe"],
    "image/": ["gif", "png", "jpeg", "bmp", "webp"],
    "image/jpeg": ["jpg"],
    "image/x-icon": ["ico"],
    "audio/": ["mpeg", "webm", "ogg", "midi", "wav"],
    "text/plain": ["txt", "*"]
}

def get_content_type(path:str):
    contentType = 'text/plain'
    log_info('getting content-type from path') ##TOKEN_TO_FIND
    if '.' in path:
        extension:str = path.split(".")[-1:][0]
        for i in contentTypes:
            if extension in contentTypes[i]:
                contentType = i
                if contentType.endswith("/"):
                    contentType += extension
                break
    log_success(f'content-type resolved to {contentType}') ##TOKEN_TO_FIND
    return contentType

def decode_querystring(data:str):
    log_info('decoding querystring') ##TOKEN_TO_FIND
    data = data.replace('+', ' ').replace('%20', ' ')#space
    data = data.replace('%2B', '+')#space
    data = data.replace('%7E', '~')#space
    references = [(i, chr(int(re.findall(r'[\d]+', i)[0]))) for i in re.findall(r'&#[\d]+;', data)]
    for ref in references:
        data = data.replace(ref[0], ref[1])
    log_success(f'querystring resolved') ##TOKEN_TO_FIND
    return data

def map_dictionary(data:str, rowSeparator:str, keySeparator:str):
    return dict([
        tuple([j.strip() for j in i.split(keySeparator, 1)])
        for i in data.split(rowSeparator) if len(i.split(keySeparator)) == 2
    ])

class HttpResponse:
    def __init__(self):
        log_info(f'response created') ##TOKEN_TO_FIND
        self.resposeStatus = 404
        self.resposeText = 'NotFound'
        self.headers = {
            "Content-Type": "text/plain",
            "Content-Length": "0",
            "Connection": "close"
        }
        self.cookieHeaders = []
        self.body = ""
        self.ended = False
        self.contentDisposition = ''
        self.cacheValue = None
        self.encoding = None
        self.lineSep = '\r\n'

    def set_encoding(self, encoding:str):
        log_info(f'encoding set to {encoding}') ##TOKEN_TO_FIND
        self.encoding = encoding
        return self

    def cache(self, cacheValue:str):
        log_info(f'cache set') ##TOKEN_TO_FIND
        self.cacheValue = cacheValue

    def end(self, data:str, status:int = None):
        self.ended = True
        self.status(status or 200)
        log_info(f'response ended') ##TOKEN_TO_FIND
        return self.write(data)

    def redirect(self, url:str, statusCode:int = None):
        self.status(statusCode or RedirectType.TEMPORARY_REDIRECT)
        log_info(f'request redirected to {url}') ##TOKEN_TO_FIND
        self.headers = {"Location": url}
        self.body = ""
        return self

    def status(self, resposeStatus:int, resposeText:str=None):
        self.resposeStatus = resposeStatus
        if resposeText == None and resposeStatus in responseCodes:
            self.resposeText = responseCodes[resposeStatus]
        else:
            self.resposeText = resposeText or "OK"
        return self

    def content_type(self, value:str):
        log_info(f'response content-type set to {value}') ##TOKEN_TO_FIND
        self.headers["Content-Type"] = value
        return self

    def json(self, data:Any):
        self.body = json.dumps(data)
        log_info(f'json response set') ##TOKEN_TO_FIND
        return self.content_type("text/json")

    def write(self, data:str):
        self.body += data
        log_info(f'data with length of {len(data)} bytes append to the body response') ##TOKEN_TO_FIND
        return self

    def html(self, data:str):
        log_info(f'html response set') ##TOKEN_TO_FIND
        return self.content_type('text/html').write(str(data))

    def read_file(self, fileName:str, contentType:str=None):
        with open(fileName, 'r') as f:
            self.body += f.read()
        log_info(f'file {fileName} read from disk') ##TOKEN_TO_FIND
        self.status(200)
        return self.content_type(contentType or get_content_type(fileName))

    def transmit_as_file(self, fileName:str, data:str, contentType:str = None, encoding:str = None):
        self.set_content_disposition('attachment', fileName).set_encoding(encoding or 'UTF-8')
        self.body = data
        log_info(f'data with length of {len(data)} bytes set as file response') ##TOKEN_TO_FIND
        self.status(200)
        return self.content_type(contentType or get_content_type(fileName))

    def set_content_disposition(self, contentDisposition:str, fileName:str = None):
        self.contentDisposition = contentDisposition
        if fileName is not None:
            self.contentDisposition += f'; fileName="{fileName}"'
        log_info(f'content disposition set to {self.contentDisposition}') ##TOKEN_TO_FIND
        return self

    def download_file(self, path:str, fileName:str, contentType:str = None, encoding:str = None):
        self.set_content_disposition('attachment', fileName).set_encoding(encoding or 'UTF-8')
        self.body = ""
        return self.read_file(path, contentType)

    def __str__(self):
        if not self.cacheValue == None:
            return self.cacheValue
        result = f"HTTP/1.1 {self.resposeStatus} {self.resposeText}{self.lineSep}"
        if 'Location' not in self.headers: self.headers["Content-Length"] = len(self.body)
        if len(self.contentDisposition or '') > 0:
            self.headers['Content-Disposition'] = self.contentDisposition 
        mappedHeaders = [f"{i}:{self.headers[i]}{self.lineSep}" for i in self.headers]
        for cookie in self.cookieHeaders:
            print(cookie)
            mappedHeaders.append(f"Set-Cookie:{cookie}{self.lineSep}")
        result += reduce(lambda a, b: a + b, mappedHeaders)
        result += f'{self.lineSep}'
        result += self.body
        log_info(f'response rendered') ##TOKEN_TO_FIND
        return result

    def set_cookie(self, name:str, value:str, durationSec:float = None, domain:str = None, path:str = None):
        cookieString = value
        if durationSec != None: 
            expireUTC = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(time.time() + durationSec))
            cookieString += f"; Expires={expireUTC}"
        if domain != None: cookieString += f"; Domain={domain}"
        if path != None: cookieString += f"; Path={path}"
        log_info(f'cookie set: {name}={cookieString}') ##TOKEN_TO_FIND
        self.cookieHeaders.append(f"{name}={cookieString}")

    def to_bytes(self) -> bytes:
        return str(self).encode(self.encoding or 'latin1')

class HttpRequest:
    __slots__ = [
        'clientAddress', 'raw', 'authorization', 
        'files', 'headers', 'body', 'method', 
        'httpVersion', 'url', 'querystring', 
        'path', 'baseUrl', 'params', 'data', 
        'headers', 'contentType', 'cookies'
    ]
    def __init__(self, raw:str, address:str):
        self.clientAddress = address
        self.load(raw)

    def load(self, raw:str):
        log_load(f'request loaded from {self.clientAddress}') ##TOKEN_TO_FIND
        self.raw = raw
        self.authorization = {}
        self.files = {}
        headerAndBody = self.raw.split('\r\n\r\n', maxsplit=1)
        self.headers = headerAndBody[0].split('\r\n')
        self.body = '' if len(headerAndBody) <= 1 else headerAndBody[1]
        firstLine = self.headers[:1][0].split(' ')
        self.headers = self.headers[1:]
        self.method = firstLine[0]
        self.httpVersion = firstLine[2] if len(firstLine) >= 2 else 'HTTP/1.1'
        self.url = firstLine[1] if len(firstLine) >= 1 else ''
        self.querystring = decode_querystring(self.url.split('?', 1)[1] if '?' in self.url else '')
        self.path = self.url.split('?')[:1][0]
        if not self.path.endswith('/'):
            self.path += '/'
        self.baseUrl = self.url if '?' not in self.url else self.url.split('?', 1)[0]
        self.params = map_dictionary(self.querystring, '&', '=')
        self.data = {}
        self.headers = dict([
            tuple([j.strip() for j in i.split(':', 1)]) for i in self.headers
            if len(i.split(':')) == 2
        ])
        self.contentType = self.headers.get('Content-Type', None)
        self.cookies = {}
        if 'Cookie' in self.headers:
            self.cookies = dict([tuple([j.strip() for j in i.split('=')]) for i in self.headers['Cookie'].split(';') if len(i.split('=')) == 2])

class ServerWorker(Thread):
    def __init__(self, action):
        Thread.__init__(self)
        self.action = action
    
    def run(self):
        self.action()

class Server(Thread):
    def __init__(self, port:int = 80, hostname:str = 'localhost', backlog: int = 5, readTimeout: float = 0.025, bufferSize: int = 1024):
        Thread.__init__(self)
        self.running = False
        self.port = port
        self.hostname = hostname
        self.backlog = backlog
        self.readTimeout = readTimeout
        self.bufferSize = bufferSize
    
    def __enter__(self):
        self.start()
    
    def __exit__(self, type, value, traceback):
        self.stop()
    
    def __del__(self):
        self.stop()
    
    def get_socket(self) -> socket.socket:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def on_receive(self, data:bytes, clientPort:socket.socket, clientAddress:str):
        raise NotImplementedError()
    
    def on_accept(self, client:socket.socket, address:str, readTimeout:int = None, closeSocket:bool = True):
        self.on_receive(self.read(client, readTimeout), client, address)
        if closeSocket:
            client.close()

    def read(self, client:socket.socket, readTimeout:int = None) -> bytes:
        data = []
        timeout = client.gettimeout()
        try:
            client.settimeout(readTimeout or self.readTimeout)
            while True:
                try:
                    buffer:bytes = client.recv(self.bufferSize)
                    if len(buffer) == 0:
                        break
                    data.extend(buffer)
                except:
                    break
        finally:
            client.settimeout(timeout)
        return bytes(data)
        
    def next_free(self, port:int, max_port=65535):
        sock = self.get_socket()
        while port <= max_port:
            try:
                sock.bind(('', port))
                sock.close()
                return port
            except OSError:
                port += 1
        else:
            raise IOError('no free ports')
    
    def run(self):
        log_warning(f'server starting...') ##TOKEN_TO_FIND
        if self.running:
            return
        self.running = True
        port = self.next_free(self.port)
        if port != self.port:
            log_warning(f'Port {self.port} already in use. Using port {port} instead.')
            self.port = port
        srv = self.get_socket()
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.hostname, self.port))
        srv.listen(self.backlog)
        log_success(f'server sucessfully started') ##TOKEN_TO_FIND
        while self.running:
            try:
                log_success(f'listening for new requests') ##TOKEN_TO_FIND
                (client, address) = srv.accept()
                log_info(f'new requests from {address}') ##TOKEN_TO_FIND
                Thread(target=(lambda :self.on_accept(client, address))).start()
            except Exception as e:
                log_error('unexpected error has occur')
    
    def cancel_listen(self):
        log_warning(f'canceling listen')
        clt = self.get_socket()
        clt.connect((self.hostname, self.port))
        clt.close()
        
    def stop(self):
        if self.running:
            log_warning(f'server stop requested')
            self.running = False
            self.cancel_listen()
            self.join()

class Bridge:
    def __init__(self, port:int, address:str = 'localhost') -> None:
        self.port = port
        self.address = address
        
    def send(self, data:str, encoding:str='latin1', bufferSize:int=1024) -> str:
        result = ''
        target = (self.address, self.port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(target)
            client.sendall(data.encode(encoding))
            while data:
                data = client.recv(bufferSize)
                if not data:
                    break
                result += data.decode(encoding)
        return result

class Proxy(Server):
    def __init__(self, port=80, connectionTimeout=None, targets = []):
        Server.__init__(self, port, connectionTimeout)
        self.targets = dict([(i, []) for i in targets])

    def onReceive(self, clientPort:int, data:str, clientAddress):
        target = self.get_target(clientAddress[0])
        result = Bridge(target[1], target[0]).send(data, 'latin1')
        clientPort.send(result.encode('latin1'))
        
    def get_target(self, address:str):
        targets = [i for i in self.targets]
        for t in targets:
            if address in self.targets[t]:
                return t
        t = random.choice(targets)
        self.targets[t].append(address)
        return t

class Session:
    def __init__(self, cookieName = None):
        self.cookieName = cookieName or 'sessionId'
        self.sessions = {}

    def ensure_session(self, req:HttpRequest, res:HttpResponse, reset:bool = False):
        sessionId = ''
        if self.cookieName not in req.cookies:
            sessionId = str(uuid.uuid4())
            res.set_cookie(self.cookieName, sessionId)
            req.cookies[self.cookieName] = sessionId
        else:
            sessionId = req.cookies[self.cookieName]
        if sessionId not in self.sessions or reset:
            self.sessions[sessionId] = {}
        return sessionId

    def get(self, req:HttpRequest, res:HttpResponse, key):
        sessionId = self.ensure_session(req, res)
        if key not in self.sessions[sessionId]:
            return None
        else:
            return self.sessions[sessionId][key]

    def set(self, req:HttpRequest, res:HttpResponse, key, value):
        sessionId = self.ensure_session(req, res)
        self.sessions[sessionId][key] = value

    def create_session(self, req:HttpRequest, res:HttpResponse):
        return RequestSession(req, res, self)

class RequestSession:
    def __init__(self, req:HttpRequest, res:HttpResponse, session:Session):
        self.req = req
        self.res = res
        self.session = session
    
    def __setitem__(self, key:str, value):
        self.session.set(self.req, self.res, key, value)

    def __getitem__(self, key:str):
        return self.session.get(self.req, self.res, key)
    
    def try_get(self, key:str, defaultValue = None):
        value = self.session.get(self.req, self.res, key)
        if value is None:
            value = defaultValue
            self.session.set(self.req, self.res, key, value)
        return value
    
    def reset_session(self):
        self.session.ensure_session(self.req, self.res, True)