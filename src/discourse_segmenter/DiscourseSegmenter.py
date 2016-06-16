'''
Created on May 10, 2015

@author: gtomar
'''
import os
from subprocess import call

class DiscourseSegmenter(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.discourse_parser_folder = "/usr0/home/gtomar/Discourse_Parser_Dist/"
        self.discourse_segmenter_script = "Discourse_Segmenter.py"
        self.discourse_segmented_file = "tmp.edu"
        
    def do_segment(self, infile, outfile, thread_id):
        os.chdir(self.discourse_parser_folder)
        command_run = call(["python", self.discourse_parser_folder + self.discourse_segmenter_script, infile])
        #print "python " + self.discourse_parser_folder + self.discourse_segmenter_script + " " + infile
        #command_run = os.system("python " + self.discourse_parser_folder + self.discourse_segmenter_script + " " + infile)
        if command_run != 0:
            print "Error in segmenting " + thread_id
        
        command_run = call(["cp", self.discourse_parser_folder + self.discourse_segmented_file, outfile]);
        if command_run != 0:
            print "Error in copying from " + self.discourse_parser_folder + self.discourse_segmented_file + " to " +  outfile 
        
        segmented_output = ""    
        try:            
            file_handle = open(outfile, 'r')
            segmented_output = file_handle.read()
        except IOError:
            print "Error: can\'t find file or read data - " + outfile
        else :
            file_handle.close()

        return segmented_output
        
        