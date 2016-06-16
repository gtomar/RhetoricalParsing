'''
Created on May 10, 2015

@author: gtomar
'''

class ArrangePosts(object):
    '''
    Class to arrange posts and comments
    '''


    def __init__(self):
        '''
        Constructor
        ''' 
        self.arranged_posts = [];
        self.arranged_posts_partitions = {};#
    
    def preorder_traversal_model1(self, post):
        if post is None:
            return
        else:
            self.arranged_posts.append(post)
            children = post.get_children()
            if children is None:
                return
            for child in children:
                self.preorder_traversal_model1(child)

    def preorder_traversal_model2(self, post):
        if post is None:
            return;
        else:
            self.arranged_posts.append(post)
            children = post.get_children()
            if children is None:
                return
            children.sort(key=lambda x: x.timestamp)
            for child in children:
                self.preorder_traversal_model2(child)

    def preorder_traversal_model3(self, post):
        if post is None:
            return;
        else:
            if post.get_partition_number() in self.arranged_posts_partitions.keys():
                self.arranged_posts_partitions[post.get_partition_number()].append(post)
            else:
                self.arranged_posts_partitions[post.get_partition_number()] = [post]    
            children = post.get_children()
            if children is None:
                return
            children.sort(key=lambda x: x.timestamp)
            for child in children:
                self.preorder_traversal_model3(child)
                    
    #model1        
    def temporal_arrangement(self, posts):
        
        for post in posts:
            self.preorder_traversal_model1(post)
        
        self.arranged_posts.sort(key=lambda x: x.timestamp)   
        return self.arranged_posts
    
    #model 2    
    def pseudo_monologic_arrangement(self, posts):

        posts.sort(key=lambda x: x.timestamp)
        for post in posts:
            self.preorder_traversal_model2(post)
            
        return self.arranged_posts
    
    #model 3    
    def poly_pseudo_monologic_arrangement(self, posts):

        posts.sort(key=lambda x: x.timestamp)
        for post in posts:
            self.preorder_traversal_model3(post)
            
        return self.arranged_posts_partitions   
    
    def get_arranged_posts(self): 
        return self.arranged_posts
    
    def get_arranged_posts_partitions(self):
        return self.arranged_posts_partitions