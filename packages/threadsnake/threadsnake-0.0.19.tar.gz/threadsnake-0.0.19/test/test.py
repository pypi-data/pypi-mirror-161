from threading import Lock
from threadsnake.myhttp.logging import LogColors
from threading import Thread
import time
from typing import Any, List, Dict
from random import random

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
        

class Progress(Thread):
    def __init__(self, length:int=25, value:int=0, interval:float=0.1, emptyCharacter:str = '.', fillCharacter:str = '|'):
        Thread.__init__(self)
        
        self.running:bool = False
        self.length:int = length
        self.value:float = value
        self.interval:float = interval
        
        self.textColor:str = LogColors.BRIGHT_FOREGROUND_WHITE
        self.barColors:List[str] = [LogColors.BRIGHT_FOREGROUND_GREEN]
        self.percentColor:str = [LogColors.BRIGHT_FOREGROUND_YELLOW, LogColors.BRIGHT_FOREGROUND_GREEN]
        
        self.animationCharacters:List[str] = [' ']
        self.animationIndex = 0
        self.size = 10
        self.emptyBarCharacter = ' '
        self.fillBarCharacter = '█'
        
        self.show:bool = True
        
    def set_message(self, text:str):
        text = ' '*self.size + text + ' '*self.size
        self.animationCharacters:List[str] = [text[:self.size] for i in range(10)] 
        self.animationCharacters += [text[i:i+self.size] for i in range(len(text)-self.size)]
    
    def set_value(self, value:float = 0):
        self.show = True
        self.value = min(max(0, value), 1)
    
    def carriage_return(self):
        print('\r', end='')
    
    def animate_text(self):
        if len(self.animationCharacters) == 0:
            return
        self.animationIndex+=1
        value = f'{self.animationCharacters[self.animationIndex%len(self.animationCharacters)]}'
        print(f'[{self.textColor}' + value.ljust(self.size) + f'{LogColors.ENDC}]', end='')

    def animate_bar(self):
        value = min(max(0, self.value), 1)
        fillValue = int(value * self.length)
        emptyValue = self.length - fillValue
        text = ''
        if value > 0:
            text += self.barColors[self.animationIndex%len(self.barColors)]
            text += self.fillBarCharacter * fillValue 
            text += LogColors.ENDC
        if value < 1:
            text += self.emptyBarCharacter * emptyValue
        print(f'[{text}]', end='')

    def animate_percent(self):
        value = int(100 * min(max(0, self.value), 1))
        text = '['
        if(self.value == 1):
            text+=self.percentColor[1]
        else:
            text+=self.percentColor[0]
        text += str(value).rjust(3) + '%' + LogColors.ENDC
        text += ']'
        print(text, end='')
        
    def run(self):
        if self.running:
            return
        self.running = True
        while self.running:
            self.print_progress()
            time.sleep(self.interval)
        else:
            self.print_progress()
    
    def print_progress(self):
        if not self.show:
            return
        self.carriage_return()
        self.animate_text()
        self.animate_bar()
        self.animate_percent()


    def finish(self):
        self.set_message('Done')
        self.set_value(1)
        self.print_progress()
        print()
        self.show = False
        self.set_message('')
        self.set_value(0)

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, type, value, traceback):
        self.stop()
    
    def __del__(self):
        self.stop()
        
    def stop(self):
        if self.running:
            self.finish()
            self.running = False
            self.join()
            
def progress(max:int=100, value:int=0, interval:float=0.1) -> Progress:
    return Progress(max, value, interval)

with SharpLock(' '):
    print('sharped locked!')
    
with Progress() as p:
    i = 0
    p.set_message('Testing the threadsnake...')
    while i < 100:
        if random() > 0.5:
            i += 1 
        p.set_value(i / 100.00)
        time.sleep(1)