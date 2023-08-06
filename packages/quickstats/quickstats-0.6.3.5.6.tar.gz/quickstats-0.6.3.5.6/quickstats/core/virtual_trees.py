from typing import Optional, List

from .decorators import semistaticmethod

class TVirtualNode:
    
    def __init__(self, name:Optional[str]=None, level:Optional[int]=0,
                 parent:Optional["TVirtualNode"]=None,
                 **data):
        self.name     = name
        self.level    = level
        self.parent   = parent
        self.prev_sibling = None
        self.next_sibling = None
        self.children = []
        self.data     = {**data}
        
    def get_number_of_children(self):
        return len(self.children)
    
    def get_data(self, key:str):
        if key not in self.data:
            raise RuntimeError(f'missing data attribute "{key}"')
        return self.data[key]
    
    @property
    def has_child(self):
        return self.get_number_of_children() > 0
    
    @property
    def first_child(self):
        if self.has_child:
            return self.children[0]
        return None
    
    @property
    def last_child(self):
        if self.has_child:
            return self.children[-1]
        return None
        
class TVirtualTree:
    
    NodeClass = TVirtualNode
    
    def __init__(self):
        self.root_node    = self.NodeClass()
        self.current_node = self.root_node
    
    def add_child(self, name:str, **data):
        child_node = self.NodeClass(name, level=self.current_node.level + 1,
                                    parent=self.current_node, **data)
        if self.current_node.has_child:
            last_child = self.current_node.last_child
            child_node.prev_sibling = last_child
            last_child.next_sibling = child_node
        self.current_node.children.append(child_node)
        return child_node
    
    @semistaticmethod
    def _to_diagram(self, source, indent:str=' '*4, level:int=0):
        if not isinstance(source, self.NodeClass):
            raise TypeError("source must be ActionNode, not %s" % (source.__class__.__name__,))
        if source.name is not None:
            string = f"{indent * level}- {source.name}\n"
        else:
            string = ""
            level  = - 1
        for child_node in source.children:
            string += self._to_diagram(child_node, indent=indent, level=level + 1)
        return string
    
    def __str__(self):
        return self._to_diagram(self.root_node)
    
    def reset(self):
        self.current_node = self.root_node
    
    def get_next(self, consider_child:bool=True):
        node = self.current_node
        if consider_child and node.has_child:
            node = node.first_child
        else:
            while True:
                if node.next_sibling is not None:
                    node = node.next_sibling
                    break
                elif node.parent is not None:
                    node = node.parent
                else:
                    node = None
                    break
        self.current_node = node
        return node