'''
Created on May 10, 2015

@author: gtomar
'''

class DocumentConstruction(object):
    '''
    Class to write arranged posts/comments into a file
    '''


    def __init__(self):
        '''
        Constructor
        '''
    
    def construct_document(self,posts,filename):
        
        try:
            file_handle = open(filename, "w")
        
            for post in posts:
                file_handle.write(post.text + "\n")
        except IOError:
            print "Error: can\'t find file or write data - " + filename
        else :
            file_handle.close()