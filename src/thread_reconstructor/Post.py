'''
Created on May 10, 2015

@author: gtomar
'''

class Post(object):
    '''
    Class for posts and comments on them in a thread
    '''

    def __init__(self, post_id, text, timestamp, partition_number, children=None, parent=None):
        '''
        Constructor
        '''
        self.post_id = post_id
        self.text = text
        self.timestamp = timestamp
        self.partition_number = partition_number
        self.children = children 
        self.parent = parent #assuming only one parent
        
    def get_post_id(self):
        return self.post_id
    
    def get_text(self):
        return self.text
    
    def get_timestamp(self):
        return self.timestamp
    
    def get_partition_number(self):
        return self.partition_number
    
    def get_children(self):
        return self.children
    
    def get_parent(self):
        return self.parent

    def add_child(self, child):
        if self.get_children() is None:
            self.children = [child]
        else:
            self.children.append(child)
    
    #def is_comment(self):
        #TBD
    
    
