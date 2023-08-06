class NodeBase:
    def __init__(self, Owner=None, Name=''):
        self.Name = Name
        self.Prev = None
        self.Next = None
        self.Owner =Owner
        self.Home = Owner
    
    def Eject(self):
        if self.Owner != None:
            self.Owner.Eject(self)

    def LinkAfter(self, TargetNode):
        if TargetNode != None and isinstance(TargetNode, NodeBase):
            if TargetNode.Next != None:
                TargetNode.Next.Prev = self
            self.Next = TargetNode.Next
            TargetNode.Next = self
            self.Prev = TargetNode
            self.Owner = TargetNode.Owner

    def LinkBefore(self, TargetNode):
        if TargetNode != None and isinstance(TargetNode, NodeBase):
            if TargetNode.Prev != None:
                TargetNode.Prev.Next = self
            self.Prev = TargetNode.Prev
            TargetNode.Prev = self
            self.Next = TargetNode
            self.Owner = TargetNode.Owner


class NodeQueue:
    def __init__(self, Owner=None, Name='Queue', Type=NodeBase, Limit=-1):
        self.Owner = Owner
        self.Name = Name
        self.Type = Type
        self.Limit = Limit
        self.Head = None
        self.Tail = None
        self.Size = 0

    def CreateNode(self):
        NewNode = self.Type(Owner=self, Name=f'{self.Name}_ChildNode')
        if self.Size <= 0:
            self.Head = NewNode
            self.Tail = NewNode
        else:
            NewNode.LinkAfter(self.Tail)
            self.Tail = NewNode
        self.Size += 1

        return NewNode

    def Pop(self):
        if self.Head == None:
            if self.Limit < 0:
                self.CreateNode()
            else:
                return None
        
        WaitNode = self.Head
        if self.Head == self.Tail:
            self.Head = None
            self.Tail = None
        else:
            self.Head = self.Head.Next
        self.Eject(WaitNode)

        return WaitNode

    def Eject(self, Node):
        if Node.Owner == self and isinstance(Node, self.Type):
            if Node.Prev != None:
                Node.Prev.Next = Node.Next
                Node.Prev = None
            if Node.Next != None:
                Node.Next.Prev = Node.Prev
                Node.Next = None
            Node.Owner = None
            self.Size -= 1 
            return 0
        else:
            return -1

    def PushBack(self, Node):
        if isinstance(Node, self.Type):
            if self.Tail != None:
                Node.LinkAfter(self.Tail)
                self.Tail = Node
            else:
                self.Head = Node
                self.Tail = Node
            Node.Owner = self
            self.Size += 1
        else:
            print('Type is incorrect')


class NodePool:
    def __init__(self, Owner=None, Name='', Type=NodeBase, Limit=-1):
        self.Owner = Owner
        self.Name = Name
        self.Type = Type
        self.Limit = Limit
        self.WaitQueue = NodeQueue(Owner=self, Name=f'{self.Name}_WaitQueue', Type=self.Type, Limit=self.Limit)
        self.LockQueue = NodeQueue(Owner=self, Name=f'{self.Name}_LockQueue', Type=self.Type, Limit=self.Limit)
        self.Generate()

    def Generate(self):
        if self.Limit > 0:
            for i in range(0, self.Limit):
                self.WaitQueue.CreateNode()

    def Request(self):
        ResultNode = None
        if self.WaitQueue.Size <= 0:
            if self.Limit < 0:
                ResultNode = self.WaitQueue.CreateNode()
            else:
                ResultNode = None
        else:
            ResultNode = self.WaitQueue.Pop()
        if ResultNode != None:
            self.LockQueue.PushBack(ResultNode)
        
        return ResultNode
    
    def Release(self, Node):
        if isinstance(Node, self.Type) and Node.Home == self.WaitQueue:
            Node.Eject()
            self.WaitQueue.PushBack(Node)

    def GetWaitSize(self):
        return self.WaitQueue.Size
    
    def GetLockSize(self):
        return self.LockQueue.Size
