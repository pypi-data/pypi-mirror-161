from typing import List, Optional
import re

from quickstats import semistaticmethod, TVirtualNode, TVirtualTree
from quickstats.utils.string_utils import split_lines, split_str

from .actions import RooProcBaseAction, RooProcNestedAction, get_action

class ActionNode(TVirtualNode):
    
    def __init__(self, name:Optional[str]=None, level:Optional[int]=0,
                 parent:Optional["DomainNode"]=None,
                 **data):
        super().__init__(name=name, level=level,
                         parent=parent, **data)
        self.action = None
        
    def construct_action(self):
        action_cls = get_action(self.name)
        if action_cls is None:
            raise RuntimeError(f'unknown action "{self.name}"')        
        main_text  = self.get_data("main_text")
        block_text = self.get_data("block_text")
        action = action_cls.parse(main_text=main_text, block_text=block_text)
        self.action = action        
        
class ActionTree(TVirtualTree):
    
    NodeClass = ActionNode
    
    def construct_actions(self):
        self.reset()
        node = self.get_next()
        while node is not None:
            node.construct_action()
            node = self.get_next()
        self.reset()
    
class RooConfigLine:
    
    def __init__(self, text:str, line_number:int):
        self.text = text
        self.line_number = line_number
        self.start_tag = self.get_start_tag()
        if self.start_tag:
            self.end_tag = None
        else:
            self.end_tag = self.get_end_tag()
    
    def get_start_tag(self):
        result = re.search(r"^\s*<(?!/)([^>]+)>\s*$", self.text)
        if result:
            return result.group(1)
        return result
    
    def get_end_tag(self):
        result = re.search(r"^\s*</([^>]+)>\s*$", self.text)
        if result:
            if not re.search(r"^\s*</(\w+)>\s*$", self.text):
                raise ValueError(f'Line {self.line_number}: invalid end tag syntax "{self.text}"')
            return result.group(1)
        return result
    
class RooConfigParser(object):
    
    def __init__(self):
        pass

    @semistaticmethod
    def _get_action_tree(self, clines_iter, action_tree:Optional[ActionTree]=None):
        if action_tree is None:
            action_tree = ActionTree()
        cline = next(clines_iter, None)
        if cline is None:
            current_node = action_tree.current_node
            if current_node.name is not None:
                if current_node.data["end_line_number"] == -1:
                    raise RuntimeError(f'unterminated start tag "{current_node.data["raw_text"]}" '
                                       f'at Line {current_node.data["start_line_number"]}')
            return action_tree
        if cline.start_tag:
            current_node = action_tree.current_node
            if current_node.name is not None:
                action = get_action(current_node.name)
                if not issubclass(action, RooProcNestedAction):
                    raise RuntimeError(f'Line {cline.line_number}: can not create action block within an unnestable '
                                       f'action block "{current_node.name}" '
                                       f'(Line {current_node.data["start_line_number"]})')
            tokens = split_str(cline.start_tag)
            action_name = tokens[0]
            if len(tokens) > 1:
                block_text = " ".join(tokens[1:])
            else:
                block_text = None
            child_node = action_tree.add_child(action_name,
                                               raw_text=cline.text,
                                               start_line_number=cline.line_number,
                                               end_line_number=-1,
                                               block_text=block_text,
                                               main_text="")
            action_tree.current_node = child_node
        elif cline.end_tag:
            current_node = action_tree.current_node
            if current_node.name is None:
                raise RuntimeError(f'Line {cline.line_number}: found close tag '
                                   f'"{cline.text}" without a start tag')
            if current_node.name != cline.end_tag:
                raise RuntimeError(f'Line {cline.line_number}: close tag '
                                   f'"{cline.text}" does not match the start tag '
                                   f'"{current_node.data["raw_text"]}" (Line {current_node.data["start_line_number"]})')
            current_node.data["end_line_number"] = cline.line_number
            action_tree.current_node = current_node.parent
        else:
            current_node = action_tree.current_node
            action = None
            if current_node.name is not None:
                action = get_action(current_node.name)
            if action and not issubclass(action, RooProcNestedAction):
                current_node.data["main_text"] += cline.text
            else:
                tokens = split_str(cline.text)
                action_name = tokens[0]
                if len(tokens) > 1:
                    main_text = " ".join(tokens[1:])
                else:
                    main_text = None
                child_node = action_tree.add_child(action_name,
                                                   raw_text=cline.text,
                                                   start_line_number=cline.line_number,
                                                   end_line_number=cline.line_number,
                                                   main_text=main_text,
                                                   block_text=None)
        return self._get_action_tree(clines_iter, action_tree)
        
    @semistaticmethod
    def parse_file(self, path:str):
        with open(path, "r") as f:
            text = f.read()
        return self.parse_text(text)        

    @semistaticmethod
    def parse_text(self, text:str):
        numbered_lines = split_lines(text, comment_string="#", remove_blank=True, with_line_number=True)
        clines = [RooConfigLine(line, line_number) for line, line_number in numbered_lines]
        clines_iter = iter(clines)
        action_tree = self._get_action_tree(clines_iter)
        return action_tree
    