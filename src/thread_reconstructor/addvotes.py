from __future__ import division
from scipy.stats.stats import pearsonr, linregress
from collections       import Counter
import csv, os, math, string
import pickle, pdb
from Post import Post
""" 
Script to add votes information to extracted features

@author: (Keith Maki)
@Version (5/13/15)
"""

##### User Parameters #####
corpusdir  = '/home/maki/Downloads/'
corpusfile = 'python_forum_Coursera.csv'

headerrows = 1
idCol     = 0
aidCol    = 1
threadCol = 2
userCol   = 3
groupCol  = 4
timeCol   = 5
textCol   = 6
permalink = 10

### End User Parameters ###
### Constant aliases for readability ###
THREAD_SNAPSHOTS = 0
THREAD_SNAPSHOT_POSTID = 0
THREAD_SNAPSHOT_USER_RECENT_ACTIVITY = 1
THREAD_SNAPSHOT_POST_HISTORY = 2
THREAD_SNAPSHOT_STRUCTURE = 3
THREAD_USER_RECENT_ACTIVITY = 1
THREAD_POST_HISTORY = 2
THREAD_STRUCTURE = 3
###

if __name__ == "__main__":
  fname = "../try.csv"
  (threads,users,posts) = loadCorpus(fname)
  DISCOURSE_PARSER_FOLDER = "/usr0/home/gtomar/Discourse_Parser_Dist/"
  fin = "features.out"
  for folder in ["1","2"]:
    lines = [line for line in csv.reader(open(os.path.join(DISCOURSE_PARSER_FOLDER+"model"+folder+"/",fin),'rb'))]
    out = csv.writer(open("features{0}.csv".format(folder),'wb'))
    def dothing(csvw,thing):
      csvw.writerow(thing)
      #print thing
    def cleanup(thing):
      return [filter(lambda x: x in string.printable, feat) for feat in line]
    dothing(out,[lines[0][0]]+lines[0][2:]+["tot votes","net votes","max votes","min votes"])
    for line in lines[1:]:
      line = [line[0]]+line[2:]
      votes = [int(posts[pid][17]) for pid in threads[line[0]][THREAD_POST_HISTORY]]
      votefeats = [sum([abs(vote) for vote in votes]),sum(votes),max(votes),min(votes)]
      dothing(out,cleanup(line)+votefeats)
      print "{0} {1} {2} {3}".format(*votefeats)
