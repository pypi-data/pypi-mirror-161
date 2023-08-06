from threading import Lock
from time import sleep

class ThreadShareData:
    ThreadLock = Lock()
    
    def ThreadLockWait(self):
        while self.ThreadLock.locked():
            sleep(0.5)