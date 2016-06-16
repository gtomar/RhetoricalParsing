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
       
    def temporal_arrangement(self, posts):
        arranged_posts = [];
        for post in posts:
            arranged_posts.append(post)
            children = post.children
            for child in children:
                arranged_posts.append(child)
        
        arranged_posts.sort(key=lambda x: x.timestamp)   
        return arranged_posts
        
    def pseudo_monologic_arrangement(self, posts):
        arranged_posts = [];
        posts.sort(key=lambda x: x.timestamp)
        for post in posts:
            arranged_posts.append(post)
            children = post.children
            children.sort(key=lambda x: x.timestamp)
            for child in children:
                arranged_posts.append(child)
            
        return arranged_posts
        
    def poly_pseudo_monologic_arrangement(self, posts):
        arranged_posts = {};
        posts.sort(key=lambda x: x.timestamp)
        for post in posts:
            if post.partition_number in arranged_posts.keys():
                arranged_posts[post.partition_number].append(post)
            else:
                arranged_posts[post.partition_number] = [post]    
            children = post.children
            children.sort(key=lambda x: x.timestamp)
            for child in children:
                if post.partition_number in arranged_posts.keys():
                    arranged_posts[child.partition_number].append(child)
                else:
                    arranged_posts[child.partition_number] = [child]
            
        return arranged_posts    
       
        