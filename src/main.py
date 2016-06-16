'''
Created on May 10, 2015

@author: gtomar
@version: May 11, 2015
'''
import pdb, os, csv
from subprocess import call
from memo import *
from thread_reconstructor import forumReaders
from document_constructor.ArrangePosts import ArrangePosts
from document_constructor.DocumentConstruction import DocumentConstruction
from discourse_segmenter.DiscourseSegmenter import DiscourseSegmenter
from ParseTree import *
global_thread_id = 0


DISCOURSE_PARSER_FOLDER  = "/usr0/home/gtomar/Discourse_Parser_Dist/"
DISCOURSE_PARSER_SCRIPT  = "Discourse_Parser.py"
DISCOURSE_SEGMENTED_FILE = "tmp.edu"
DISCOURSE_SEGMENTED_TAGS = "tmp.tag"
DISCOURSE_SEGMENTED_TOKS = "tmp.tok"
DISCOURSE_SEGMENTED_CHPS = "tmp.chp"
DISCOURSE_PARSED_FILE    = "tmp_sen.dis"

outfile      = "features.out"

def read_file(filename):
    try:            
        file_handle = open(filename, 'r')
        output = file_handle.read()
    except IOError:
        print "Error: can\'t find file or read data - " + filename
        return ""
    else :
        file_handle.close()
        
    return output

def copy_file(source, destination):
    command_run = call(["cp", source, destination]);
    if command_run != 0:
        print "Error in copying from " + source + " to " + destination
         
def split_newlines(func):
    def inner(inputs):
        return "\n".join(func(zip(*[el.split("\n") for el in inputs])))
    return inner

def empty_file(filename):
    command_run = os.system("cat /dev/null> " + filename);
    if command_run != 0:
        print "Error in emptying " + filename

def write_file(filename, text):
    try:
        file_handle = open(filename, "w")
        file_handle.write(text)
    except IOError:
            print "Error: can\'t find file or write data - " + filename
    else :
        file_handle.close()       
        
@split_newlines
@memo_iterable
@memo_pickle_first_to_file("/usr0/home/gtomar/RSTParse.cache")
def do_parse(segmented_text):
 
    print "Writing inputs for \n"+\
          "EDUS: {0}\nTAGS: {1}\nTOKS: {2}\nCHPS: {3}".format(*segmented_text)+\
           "to tmp.*\n***********************************************"
    write_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_FILE, segmented_text[0])
    write_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_TAGS, segmented_text[1])
    write_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_TOKS, segmented_text[2])
    write_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_CHPS, segmented_text[3])
    
    command_run = call(["python", DISCOURSE_PARSER_FOLDER + DISCOURSE_PARSER_SCRIPT,DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_FILE])
    if command_run != 0:
        print "Error in parsing " + thread_id
        print segmented_text
    
    try:            
        file_handle = open(DISCOURSE_PARSER_FOLDER + DISCOURSE_PARSED_FILE, 'r')
        parsed_output = file_handle.read()
        print "Read {0} from tmp_sen.dist\n***********************************************".format(parsed_output)
    except IOError:
        print "Error: can\'t find file or read data - " + DISCOURSE_PARSER_FOLDER + DISCOURSE_PARSED_FILE
    else :
        file_handle.close()

    return parsed_output

    

if __name__ == "__main__":
    
    print "Entry point !"
    
    #Thread construction (Re ??)
    threads = forumReaders.coursera("../try.csv")
    
    #TO_DO: Disagreement detection
     
    #Feature Output
    output1 = csv.writer(open(os.path.join(DISCOURSE_PARSER_FOLDER+"model1/",outfile),'wb'))
    output2 = csv.writer(open(os.path.join(DISCOURSE_PARSER_FOLDER+"model2/",outfile),'wb'))

    for output in [output1,output2]:
        output.writerow(["ThreadID","Thread","In-order Unit","In-order Depth","Leaf Unit","Leaf Depth","Depth 1 relations","Depth 2 relations","In-order relations"])
    
    for thread_id in threads.keys():
        #if thread_id == "1200" or thread_id == "2311" or thread_id == "290":
        #if thread_id not in ["1296", "2030", "2313", "2315", "2318", "340" , "341", "345", "343", "346", "348" , "592", "643"]: 
        #    continue
        #if(read_file(DISCOURSE_PARSER_FOLDER + "model1/" + thread_id + ".dist")!="" and read_file(DISCOURSE_PARSER_FOLDER + "model2/" + thread_id + ".dist")!=""):
        #    print "skipped " + thread_id
        #    continue
        arrange_posts_model1 = ArrangePosts()
        arrange_posts_model2 = ArrangePosts()
        arrange_posts_model3 = ArrangePosts()
    
        document_constructor = DocumentConstruction()
    
        discourse_segmenter = DiscourseSegmenter()
    
        post = threads[thread_id]
        global_thread_id = thread_id
        print "#################### Thread " + thread_id + " ############################"
        
        
        empty_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_FILE)
        empty_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_PARSED_FILE)
        
        #model1
        model1_raw_file = DISCOURSE_PARSER_FOLDER + "model1/" + thread_id + ".raw"
        model1_segmented_file = DISCOURSE_PARSER_FOLDER + "model1/" + thread_id + ".edu"
        model1_parsed_file = DISCOURSE_PARSER_FOLDER + "model1/" + thread_id + ".dist"
        arrange_posts_model1.temporal_arrangement(post)
        arranged_posts1 = arrange_posts_model1.get_arranged_posts()
        document_constructor.construct_document(arranged_posts1, model1_raw_file)
        # segment and prepare to parse
        segmented_edus1 = discourse_segmenter.do_segment(model1_raw_file, model1_segmented_file, thread_id);
        segmented_tags1 = read_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_TAGS)
        segmented_toks1 = read_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_TOKS)
        segmented_chps1 = read_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_CHPS)
        # parse
        print "Segmented: " + segmented_edus1
        parsed_text1 = do_parse([segmented_edus1,segmented_tags1,segmented_toks1,segmented_chps1])
        print "Parsed: " + parsed_text1

        
        write_file(model1_parsed_file,parsed_text1);
        print "Parsed file: " + read_file(model1_parsed_file)
        
        try:
            treeParse1 = parseRSTForest(parsed_text1)
            output1.writerow([thread_id," EDU_BREAK ".join([tree.toString() for tree in treeParse1])]+[" ".join(feature) for feature in zip(*[tree.extractTraversalFeatures() for tree in treeParse1])])
            
        except ParseError as e:
            print "Parse Error " + thread_id + ": " + str(e)
        except Exception as ex:
            print "Unexpected Error: {0}".format(type(ex).__name__)
        empty_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_FILE)
        empty_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_PARSED_FILE)
        
        #model2
        model2_raw_file = DISCOURSE_PARSER_FOLDER + "model2/" + thread_id + ".raw"
        model2_segmented_file = DISCOURSE_PARSER_FOLDER + "model2/" + thread_id + ".edu"
        model2_parsed_file = DISCOURSE_PARSER_FOLDER + "model2/" + thread_id + ".dist"
        arrange_posts_model2.pseudo_monologic_arrangement(post)
        arranged_posts2 = arrange_posts_model2.get_arranged_posts()
        document_constructor.construct_document(arranged_posts2, model2_raw_file)
        segmented_edus2 = discourse_segmenter.do_segment(model2_raw_file, model2_segmented_file, thread_id);
        segmented_tags2 = read_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_TAGS)
        segmented_toks2 = read_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_TOKS)
        segmented_chps2 = read_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_CHPS)
        # parse
        print "Segmented: " + segmented_edus2
        parsed_text2 = do_parse([segmented_edus2,segmented_tags2,segmented_toks2,segmented_chps2])
        print "Parsed: " + parsed_text2
        
        write_file(model2_parsed_file,parsed_text2)
        try: 
            treeParse2 = parseRSTForest(parsed_text2)
            output2.writerow([thread_id," EDU_BREAK ".join([tree.toString() for tree in treeParse2])]+[" ".join(feature) for feature in zip(*[tree.extractTraversalFeatures() for tree in treeParse2])])
        except ParseError as e:
            print "Parse Error " + thread_id + ": " + str(e)
        except Exception as ex:
            print "Unexpected Error: {0}".format(type(ex).__name__)
        
        
        empty_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_SEGMENTED_FILE)
        empty_file(DISCOURSE_PARSER_FOLDER + DISCOURSE_PARSED_FILE)
                
        #model3
        '''
        arrange_posts_model3.temporal_arrangement(post)
        arranged_posts = arrange_posts_model3.get_arranged_posts()
        for partition_number in arranged_posts:
            model3_raw_file = DISCOURSE_PARSER_FOLDER + "model3/" + thread_id + "_" + partition_number + ".raw"
            model3_segmented_file = DISCOURSE_PARSER_FOLDER + "model3/" + thread_id + "_" + partition_number + ".edu"
            model3_parsed_file = DISCOURSE_PARSER_FOLDER + "model3/" + thread_id + "_" + partition_number + ".dist"
            document_constructor.construct_document(arranged_posts[partition_number], model3_raw_file)
            segmented_text3 = discourse_segmenter.do_segment(model3_raw_file, model3_segmented_file, thread_id);
            parsed_text3 = do_parse(segmented_text3)
            copy_file(DISCOURSE_PARSER_FOLDER + "tmp.dist", model3_parsed_file);
            try:
                treeParse3 = parseRSTForest(parsed_text3)
                output.writerow([thread_id," EDU_BREAK ".join([tree.toString() for tree in treeParse3])]+[" ".join(feature) for feature in zip(*[tree.extractTraversalFeatures() for tree in treeParse3])])
            except ParseError as e:
                print "Parse Error " + thread_id + ": " + e
            except Exception as ex:
                print "Unexpected Error: {0}".format(type(ex).__name__)
        '''
              
        
    
