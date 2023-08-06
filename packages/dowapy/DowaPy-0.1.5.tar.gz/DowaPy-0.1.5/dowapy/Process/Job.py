from threading import Thread, Lock
from time import sleep

from ..Data.Events import CallbackEvent
from ..Data.Nodes import NodeBase, NodeQueue
from ..Data.ShareData import ThreadShareData
from .Worker import WorkerNode, WorkerPool


class SafetyLock:
    ThreadLock = Lock()
    
    def ThreadLockWait(self):
        while self.ThreadLock.locked():
            sleep(0.5)


class JobNode(NodeBase):
    def __init__(self, Owner=None, Name='', Job=None):
        super().__init__(Owner, Name)
        self.Job = Job
        self.StartCallback = CallbackEvent()
        self.EndCallback = CallbackEvent()
    
    def Release(self, *args):
        self.EndCallback.Emit(self)


class JobManager(ThreadShareData, SafetyLock):
    def __init__(self, WorkerLimit=5):
        self.CurrentJob = None
        
        self.JobQueue =  NodeQueue(Owner=self, Name='JobQueue', Type=JobNode, Limit=-1)
        self.WorkQueue = NodeQueue(Owner=self, Name='WorkQueue', Type=JobNode, Limit=-1)
        self.DoneQueue = NodeQueue(Owner=self, Name='DoneQueue', Type=JobNode, Limit=-1)
        
        self.WorkerPool = WorkerPool(Owner=self, Name='WorkerPool',Limit=WorkerLimit)
        
        self.JobManagerThread = Thread(name='JobManager_Thread',target=self.Update, daemon=True)
        self.JobManagerThread.start()

    def Reserve(self, JobInfo):
        self.ThreadLockWait()
        self.ThreadLock.acquire()
        assert JobInfo != None
        NewJobNode = self.JobQueue.CreateNode()
        NewJobNode.Job = JobInfo
        NewJobNode.EndCallback.Connect(self.Release)
        self.Debug()
        self.ThreadLock.release()
        
    def Release(self, Node):
        if isinstance(Node, JobNode):
            Node.Eject()
            self.DoneQueue.PushBack(Node)
        elif isinstance(Node, WorkerNode):
            self.WorkerPool.Release(Node)
        self.Debug()
    
    def Debug(self):
        print(f'Current JobQueue Size = {self.JobQueue.Size}')
        print(f'Current WorkQueue Size = {self.WorkQueue.Size}')
        print(f'Current DoneQueue Size = {self.DoneQueue.Size}')
        print(f'Current WorkerPool Size = {self.WorkerPool.GetWaitSize()}, {self.WorkerPool.GetLockSize()}')
    
    def Update(self):
        while True:
            sleep(0.5)
            if self.JobQueue.Size > 0 and self.CurrentJob == None:
                self.ThreadLockWait()
                self.ThreadLock.acquire()
                while self.JobQueue.Size > 0:
                    Worker = self.WorkerPool.Request()
                    if Worker == None:
                        break
                    CurrentJob = self.JobQueue.Pop()
                    CurrentJob.Job.PostProc.Connect(CurrentJob.Release)
                    Worker.Run(CurrentJob.Job)
                    self.WorkQueue.PushBack(CurrentJob)
                self.ThreadLock.release()
                




















# class JobNode(NodeBase, JobEvent, ThreadShareData):
#     def __init__(self, Owner=None, Name='', Job=None):
#         super().__init__(Owner, Name)
#         self.Job = Job
#         self.WorkStatus = WorkStatus.Wait
#         self.Thread = Thread(target=self.Update, daemon=True)
    
#     def Run(self):
#         super().Run()
#         if self.WorkStatus == WorkStatus.Wait:
#             self.WorkStatus == WorkStatus.Run
#             self.Thread.start()
    
#     def Update(self):
#         self.Job.PreProc.Emit()
#         self.Job.UpdateProc.Emit()
#         self.Job.PostProc.Emit()
#         self.WorkStatus = WorkStatus.Done
#         self.ThreadLockWait()
#         self.ThreadLock.acquire()
#         super().Release()
#         self.ThreadLock.release()


# class JobQueue(NodeQueue, ThreadShareData):
#     def __init__(self, Owner=None, Name=''):
#         super().__init__(Owner, Name, Type=JobNode, Limit=-1)


# class JobManager(ThreadShareData):
#     def __init__(self, WorkerLimit=5):
#         self.JobQueue = JobQueue(self, 'JobQueue')
#         self.WIPQueue = JobQueue(self, 'WIPQueue')
#         self.DoneQueue = JobQueue(self, 'DoneQueue')
#         #self.WorkerPool = PoolBase(WorkerNode, WorkerLimit)
#         self.JobThread = Thread(name='JobManager_Thread',target=self.Update, daemon=True)
#         self.CurrentJob = None
#         self.JobThread.start()

#     def Request(self, JobInfo):
#         NewJobNode = self.JobQueue.CreateNode()
#         NewJobNode.Job = JobInfo
#         NewJobNode.EndCallback.Connect(self.Release)
        
#     def Release(self, Node):
#         Node.Eject()
#         self.DoneQueue.PushBack(Node)
        
#     def Update(self):
#         while True:
#             sleep(0.5)
#             print(f'Current JobQueue Size = {self.JobQueue.Size}')
#             print(f'Current WIPQueue Size = {self.WIPQueue.Size}')
#             print(f'Current DoneQueue Size = {self.DoneQueue.Size}')
            
#             if self.JobQueue.Size > 0 and self.CurrentJob == None:
#                 self.CurrentJob = self.JobQueue.Pop()
#                 self.CurrentJob.Run()
#                 self.WIPQueue.PushBack(self.CurrentJob)
#                 self.CurrentJob = None 
