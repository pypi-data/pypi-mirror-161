from threading import Thread

# from DowaPy.Process.Job import JobNode

from ..Data.Events import CallbackEvent, WorkerEvent
from ..Data.Nodes import NodeBase, NodeQueue, NodePool
from ..Data.Enums import WorkStatus
from ..Data.ShareData import ThreadShareData


class WorkerNode(NodeBase, WorkerEvent, ThreadShareData):
    def __init__(self, Owner=None, Name=''):
        super().__init__(Owner, Name)
        self.Job = None
        self.WorkStatus = WorkStatus.Wait
        self.StartCallback = CallbackEvent()
        self.EndCallback = CallbackEvent()
        
        self.Thread = Thread(name=f'Thread_{self.Name}', target=self.Update, daemon=True)
    
    def Run(self, Job):
        self.Job = Job
        self.StartCallback.Emit(self) 
        if self.WorkStatus == WorkStatus.Wait:
            self.WorkStatus == WorkStatus.Run
            try:
                self.Thread.start()
            except RuntimeError:
                self.ThreadReset()
                self.Thread.start()
                
    def ThreadReset(self):
        self.Thread = Thread(name=f'Threa_{self.Name}', target=self.Update, daemon=True)
    
    def Update(self):
        self.Job.PreProc.Emit()
        self.Job.UpdateProc.Emit()
        self.Job.PostProc.Emit()
        self.WorkStatus = WorkStatus.Done
        self.ThreadLockWait()
        self.ThreadLock.acquire()
        self.EndCallback.Emit(self)
        self.ThreadLock.release()
        print(f'{self.Name} Work Done')
        
    def Reset(self):
        self.WorkStatus = WorkStatus.Wait
        # self.Job = None
        self.ThreadReset()


class WorkerPool(NodePool):
    def __init__(self, Owner=None, Name='', Limit=-1):
        super().__init__(Owner, Name, WorkerNode, Limit)
        
    def Generate(self):
        if self.Limit > 0:
            for i in range(0, self.Limit):
                CurrentNode = self.WaitQueue.CreateNode()
                CurrentNode.EndCallback.Connect(self.Release)
                
    def Release(self,Node):
        if isinstance(Node, self.Type) and Node.Home == self.WaitQueue:
            Node.Eject()
            Node.Reset()
            self.WaitQueue.PushBack(Node)