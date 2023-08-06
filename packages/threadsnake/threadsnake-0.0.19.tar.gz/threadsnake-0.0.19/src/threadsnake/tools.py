from asyncio.subprocess import PIPE
import subprocess
from threading import Lock
from typing import Any, Dict

class PhpServer:
    def __init__(self, path:str, port:int = 80, address:str= 'localhost', phpBinPath:str='php') -> None:
        self.path:str = path
        self.port:int = port
        self.address:str = address
        self.process:subprocess.Popen = None
        self.pid:int = None
        self.phpBinPath = phpBinPath
        
    def start(self):   
        arguments = [
            f'{self.phpBinPath}',
            f'--server',
            f'{self.address}:{self.port}'
        ]
        path = self.path
        self.process = subprocess.Popen(arguments, stdout=PIPE, stderr=PIPE, cwd=path)
        self.pid = self.process.pid
        return self
    
    def stop(self):
        self.process.kill()
        
class SharpLockLocks:
    locks:Dict[int, Lock] = dict()  

class SharpLock(SharpLockLocks):
    def __init__(self, obj:Any):
        self.lockid = id(obj)
        if self.lockid not in SharpLockLocks.locks:
            SharpLockLocks.locks[self.lockid] = Lock()
    
    def __enter__(self):
        SharpLockLocks.locks[self.lockid].acquire()
        return self
    
    def __exit__(self, type, value, traceback):
        SharpLockLocks.locks[self.lockid].release()