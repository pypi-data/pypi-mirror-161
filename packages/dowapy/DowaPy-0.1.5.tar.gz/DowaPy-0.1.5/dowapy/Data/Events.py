class CallbackEvent:
    def __init__(self, *args):
        self.Type = args
        self.Events = []
        
    def Connect(self, Func):
        if callable(Func):
            self.Events.append(Func)
    
    def Emit(self, *args):
        for Event in self.Events:
            if callable(Event):
                Event(*args)

class WorkerEvent:
    def __init__(self):
        self.PreProc = CallbackEvent()
        self.UpdateProc = CallbackEvent()
        self.PostProc = CallbackEvent()