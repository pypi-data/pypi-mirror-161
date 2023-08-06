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
import socket
import time
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, List, Union

from threadsnake.myhttp.logging import log_error, log_info, log_load, log_success, log_warning

from .myhttp import Server, HttpRequest, HttpResponse, Session, RequestSession
from uuid import uuid4
import os
import re
from importlib import __import__ as importpy
import importlib.util



'''
Loads a library from specified path.
Thanks to 
[[https://stackoverflow.com/users/7779/sebastian-rittau|Sebastian Rittau|target="_blank"]] and 
[[https://stackoverflow.com/users/3907364/raven|Raven|target="_blank"]]
'''
def import_library(name, path, modulePreload:Callable[[ModuleType],None] = None):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    if modulePreload is not None:
        modulePreload(mod)
    spec.loader.exec_module(mod)
    return mod

class RouterTemplate:
    def __init__(self) -> None:
        self.R:Router = None

class Router:
    def __init__(self):
        #print('router created')
        self.routes = {}
        self.callbackMutator:CallbackMutator = lambda a: a
        self.logRouteConfig = False

    def register_function(self, httpMethod:str, route:str):
        ref:Router = self
        if not route.endswith('/'):
            route += '/'
        if not route.startswith('/'):
            route = '/' + route
        while '//' in route:
            route = route.replace('//', '/')
        if self.logRouteConfig:
            log_warning(f"Route configured [{httpMethod.upper()}] {route}") ##TOKEN TO FIND
        def inner(function:Callback) -> Callback:
            function = self.callbackMutator(function)
            if httpMethod.upper() not in ref.routes:
                ref.routes[httpMethod.upper()] = {route: function}
            else:
                ref.routes[httpMethod.upper()][route] = function
            return function
        return inner
    
    def use_globally(self, mutator):
        callbackMutator = self.callbackMutator
        def innerMutator(c):
            return mutator(callbackMutator(c))
        self.callbackMutator = innerMutator
        return self

    def get(self, route):
        return self.register_function('GET', route)

    def post(self, route):
        return self.register_function('POST', route)
    
    def put(self, route):
        return self.register_function('PUT', route)
    
    def delete(self, route):
        return self.register_function('DELETE', route)

    def configure(self, handler):
        self.stack.append(handler)
        return self

    def use_router(self, router, root):
        for method in router.routes:
            for action in router.routes[method]:
                self.register_function(method,f'{root}{action}')(router.routes[method][action])
        return self

    def serve_statically(self, route:str, content:Union[str, Callable[[Any, HttpRequest, HttpResponse],str]], encoding:str=None):
        def sub(s:str, ss:str)->str:
            return s if ss not in s else s[s.index(ss)+1:]
        fileName = sub(sub(route, '/'), '\\')
        def callback(app:Application, req:HttpRequest, res:HttpResponse):
            data = content if isinstance(content, str) else content(app, req, res)
            res.transmit_as_file(fileName, data, encoding=encoding)
        self.get(route)(callback)
        return self

    def __getattr__(self, method):
        def inner(route):
            return self.register_function(method.upper(), route)
        return inner


class Application(Server, Router):
    def __init__(self, port: int = 80, hostname: str = 'localhost', backlog: int = 5, readTimeout: float = 0.1, bufferSize: int = 1024):
        Server.__init__(self, port, hostname, backlog, readTimeout, bufferSize)
        Router.__init__(self)
        self.stack = []
        self.session:RequestSession = None
        self.logRouteConfig = True
        
    def cli_loop(self, main_event: Callable):
        self.start()
        continueLoop = True
        while(continueLoop):
            try:
                continueLoop = main_event()
            except KeyboardInterrupt as e:
                print('[CLI EXIT]')
                break
            finally:
                self.stop()
                
    def wait_exit(self, message:str = 'press [Enter] to exit...'):
        try:
            self.start()
            log_info(message)
            input('')
        except:
            pass
        finally:
            self.stop()

    def on_receive(self, data:bytes, clientPort:socket.socket, clientAddress):
        data_s = data.decode('latin1')
        if(len(data_s) == 0): return
        req = None
        res = HttpResponse()
        try:
            req = HttpRequest(data_s, clientAddress)
        except Exception as e:
            log_error(e) ##TOKEN TO FIND
            res.status(403, "BadRequest")
            clientPort.send(str(res).encode('latin1'))
            return
        
        if req.headers.get('Connection', '').lower() == 'keep-alive':
            log_warning(f'Connection from {clientAddress} requested kept-alive!')
            chunk:bytes = self.read(clientPort, 0.2 if len(data_s) < 128 else 1)
            if len(chunk) != 0:
                self.on_receive(b''.join([data, chunk]), clientPort, clientAddress)
                return
            else:
                log_success(f'{clientAddress} ended...')

        log_info(f'response pipeline created') ##TOKEN TO FIND
        stack = self.stack.copy()

        def next():
            if len(stack) > 0 and not res.ended:
                stack.pop()(self, req, res, next)
        
        if ':' in req.path:
            log_warning(f'potential query:pass params detected') ##TOKEN TO FIND
            pathParts = req.path.split('/')
            newPath = []
            for i in pathParts:
                queryPassParam = i.split(':')
                if len(queryPassParam) == 2:
                    log_load(f'query:pass param {queryPassParam[0]} resolved to {queryPassParam[1]}') ##TOKEN TO FIND
                    req.params[queryPassParam[0]] = queryPassParam[1]
                else:
                    newPath.append(i)
            req.path = '/'.join(newPath)

        if req.method in self.routes:
            log_success(f'method {req.method} found in registered routes') ##TOKEN TO FIND
            regularPaths = [i for i in self.routes[req.method]]
            for route in regularPaths:
                pattern = route
                pattern = re.sub(r"{([\w]+)\:int}", r"(?P<\1>[-]?[\\d]+)", pattern)
                pattern = re.sub(r"{([\w]+)\:float}", r"(?P<\1>[-]?[\\d]+[\\.]?[\\d]?)", pattern)
                pattern = re.sub(r"{([\w]+)\:re\(([\w\W]+?)\)}", r"(?P<\1>\2)", pattern)
                pattern = re.sub(r"{([\w]+)}", r"(?P<\1>[\\w]+)", pattern)
                pattern = "^" + pattern + "$"
                match = re.match(pattern, req.path)
                if match:
                    log_success(f'request {req.url} matches {route}') ##TOKEN TO FIND
                    handler = self.routes[req.method][route]
                    queryParams = match.groupdict()
                    for i in queryParams:
                        log_load(f'param {i} set to {queryParams[i]}') ##TOKEN TO FIND
                        req.params[i] = queryParams[i]
                    log_success(f'middleware for {route} add to pipeline') ##TOKEN TO FIND
                    def middleware(app, req, res, next):
                        res.status(200)
                        handler(app, req, res)
                        next()
                    stack.append(middleware)
                    break
        stack.reverse()
        log_info(f'pipeline begin') ##TOKEN TO FIND
        next()
        log_info(f'pipeline end') ##TOKEN TO FIND
        clientPort.send(res.to_bytes())

Middleware = Callable[[Application, HttpRequest, HttpResponse, Callable[[], None]], None]
Callback = Callable[[Application, HttpRequest, HttpResponse], None]
ServerCallback = Callable[[HttpRequest, HttpResponse], None]
DictProvider = Callable[[], Dict[str, Any]]
CallbackMutator = Callable[[Callback], Callback]

def build_application(port: int, middlewares: List[Middleware] = None, routers: Dict[str, Router] = None):
    app = Application(port)
    for m in middlewares or []:
        app.configure(m)
    for r in routers or dict():
        app.use_router(routers[r], r)
    return app

def create_server(port:int, callback:ServerCallback) -> Application:
    app = Application(port)
    def innerMiddleware(application:Application, req:HttpRequest, res:HttpResponse, next):
        callback(req, res)
        next()
    app.configure(innerMiddleware)
    return app


routers:Dict[str, ModuleType] = {}
def load_router(name, path) -> RouterTemplate:
    def assign_router(mod:ModuleType) -> None:
        global routers
        mod.R = Router()
        routers[name] = mod
    return import_library(name, path, assign_router)

def export(caller:str) -> Router:
    global routers
    return routers[caller].R
    
def routes_to(name:str):
    path = name if name.endswith('.py') else name + '.py'
    libName = 'threadsnake.router.to_'+str(uuid4()).replace('-', '')
    return load_router(libName, path).R

def routes_to_folder(folder:str = 'routers', onExcept:Callable[[Exception,], None] = None) -> Dict[str, Router]:
    result:Dict[str, Router] = {}
    files = os.listdir(folder)
    for f in [(i[:-3], os.sep.join(folder, i)) for i in files if i.endswith('.py')]:
        try:
            result = result[f[0]] = load_router(f[0], f[1]).R
        except Exception as e:
            if onExcept is not None:
                onExcept(e)
    return result
