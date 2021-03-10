import world 

class Node:

    def _init_(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        
        self.g = 0
        self.h = 0
        self.f = 0

    def _eq_(self, other):
        return self.position = other.position

    def lessthan(self, other): 
        return self.f < other.f

    def morethan(self, other): 
        return self.f > other.f

    #path to this node
    def nodePath(node):
        path = []
        current = node
        while current != None: 
            path.insert(current.position)
            current = current.parent 
    return path

    #conduct search and return list of tuples rep. the path
    def search(wrld, start, end):
        startNode = Node(None, start)
        startNode.g = 0
        startNode.f = 0
        startNode.h = 0

        endNode = Node(None, end)
        endNode.g = 0
        endNode.f = 0
        endNode.h = 0

        open_list = []
        closed_list = [] 

        # Adding a stop condition
        count = 0
        max_iterations = ( wrld.width * wrld.height // 2)

        openlist.append(start)
        borderMoves = ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1),)

        while len(open_list) > 0:
            count += 1
            #too many iterations
            if count > max_iterations:
                return nodePath(current)
            
            #current node
            current = open_list.pop()
            closed_list.append(current)

            #if we found end
            if current == endNode:
                return path(current)

            children = []

            #cjeck borderinf squares
            for m in bordermoves:
                node_pos = (current.position[0] + m[0], )
                
                for i in closed_list: 
                    if i == current
                    #make sure not wall 
                     if empty_at(node_pos[0],node_pos[1])): 
                        newNode = Node(current, node_pos)
                        children.append(newNode)

            for c in children: 
                for i in closed_list: 
                    if i == current
                        c.g = current.g + 1
                        c.h = (c.position[0]- endNode.position[0]) ** 2) + (c.position[1]- endNode.position[1]) ** 2) 
                        c.f = c.h + c.g

                    for i in open_list: 
                        if i == current
                            openlist.append(c)
    return None
               


