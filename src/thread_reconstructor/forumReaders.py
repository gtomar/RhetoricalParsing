from __future__ import division
from scipy.stats.stats import pearsonr, linregress
from collections       import Counter
import csv, os, math
import pickle, pdb
from Post import Post
""" 
Library code to recover implicit thread structure using cues in posts
  The final part extracts threads which include posts
  referencing at least two users by name

@author: (Keith Maki)
@Version (5/10/15)
"""

##### User Parameters #####
corpusdir  = '/home/maki/Downloads/'
corpusfile = 'python_forum_Coursera.csv'

Format

### End User Parameters ###
###########################
########################################
### Constant aliases for readability ###
THREAD_SNAPSHOTS = 0
THREAD_SNAPSHOT_POSTID = 0
THREAD_SNAPSHOT_USER_RECENT_ACTIVITY = 1
THREAD_SNAPSHOT_POST_HISTORY = 2
THREAD_SNAPSHOT_STRUCTURE = 3
THREAD_USER_RECENT_ACTIVITY = 1
THREAD_POST_HISTORY = 2
THREAD_STRUCTURE = 3
########################################

def avg(l, ind, cfun): 
  if len(l) > 0:
    return sum([cfun(el[ind]) for el in l])/len(l)
  return 0

class ForumParser( object ):
  headerrows   = 1
  idCol        = 0
  aidCol       = 1
  threadCol    = 2
  userCol      = 3
  groupCol     = 4
  timeCol      = 5
  textCol      = 6
  permalinkCol = 10

  def fixIDErrors( self, line, posts, openPID, openCID ):
    """
    stub for a void method to enforce metadata sanity
    currently does nothing
    must be overridden by parser to implement specific behavior
    """
    return openPID, openCID

  def newThread( self ):
    return ([],{},[],{"top":[]})

  def loadCorpus( self, fname ):
    # load corpus
    fin = csv.reader( open( fname, 'rb' ) )
    # strip header rows
    for i in range( headerrows ): header = fin.next()

    #Load pid, aid, tid, uid, gid, timestamp, text, [other info], names
    header = [ header[ self.idCol ], header[ self.aidCol ], 
               header[ self.threadCol ], header[ self.userCol ], "group_id", 
               header[ self.timeCol ], header[ self.textCol ] ]
           + [ header[i] for i in range(17) if not i in 
               [ self.idCol, self.aidCol, self.threadCol, 
                 self.userCol, self.timeCol, self.textCol ] ] 
           + [ "Names" ]
    header[ self.textCol ] = header[ self.textCol ].replace( "\xc2\xa0", " " )
    # extract lines sorted by timestamp
    lines   = sorted( [ [ line[ self.idCol ], line[ self.aidCol ], 
                          line[ self.threadCol ], line[ self.userCol ], 0, 
                          line[ self.timeCol ], line[ self.textCol ] ] 
                      + [ line[i] for i in range(17) 
                               if not i in [ self.idCol, self.aidCol, 
                                             self.threadCol, self.userCol, 
                                             self.timeCol, self.textCol ] ] 
                        for line in fin ], key=lambda x:x[5] )

    # Replace any consecutive whitespace with a single space
    for line in lines:
      line[ self.textCol ] = line[ self.textCol ].replace("\xc2\xa0"," ")
      line[ self.textCol ] = " ".join( 
                        [ el.strip() for el in line[ self.textCol ].split() 
                                            if el.strip() ] )

    # Prepare threads
    threads = {}
    users   = {}
    posts   = {}
    openPID = 0
    openCID = 0
    for line in lines:
   
      # id sanity enforcement
      openPID, openCID = fixIDErrors( line, posts, openPID, openCID )

      postID = line[ self.idCol ]
      userID = line[ self.userCol ]
      thread = threads.get( line[ self.threadCol ], newThread() )
      threadSnapshot = ( postID, thread[ THREAD_USER_RECENT_ACTIVITY ].copy(),
                         list( thread[ THREAD_POST_HISTORY ] ),
                         dict( thread[ THREAD_STRUCTURE ] ) )
      thread[ THREAD_SNAPSHOTS ].append( threadSnapshot )
      thread[ THREAD_USER_RECENT_ACTIVITY ][ userID ] = postID
      thread[ THREAD_POST_HISTORY ].append( postID )

      # Build thread structure metadata information
      if "post" in postID:
        thread[ THREAD_STRUCTURE ][ "top" ].append( postID )
      else:
        aid = line[ self.aidCol ]
        if not aid:
          # we were unable to find ancestor metadata
          # assume post responds to most recent post in thread
          aid = thread[ THREAD_POST_HISTORY ][ -1 ]
        if aid not in thread[ THREAD_STRUCTURE ]:
          thread[ THREAD_STRUCTURE ][ aid ] = []
        thread[ THREAD_STRUCTURE ][ aid ].append( postID )

      
      users.get( userID, [] ).append( postID )  
      posts[ postID ] = line

    return ( threads, users, posts )

  def recoverStructure( self, threads, users, posts ):

    aliases = {}
    for user in users.keys():
      if " " in user:
        aliases[ user ] = set( [ name.capitalize() for name in user.split() ]\
                               + user.lower().split() + user.split() )
      else:
        aliases[ user ] = set( [ user.capitalize() ] + [ user.upper() ]\
                               + [ user.lower() ] )

  
    def matchNamesInSet( text, names ):
      try:
        clauses  = [ clause for chunk  in text.split( "." ) 
                            for sent   in chunk.split( "!" ) 
                            for clause in sent.split( "," ) if clause ]
        return set( [ name  for clause in clauses 
                            for word   in clause.split() 
                            for name   in names
                       if word.lower() in aliases[ name ]
                  and not word.lower() == username.lower().split()[ 0 ] ] )
      except:
        pdb.set_trace()

    # Identify posts referenced by other contributions
    counts = {}
    names_matched = {}
    threadsInfo = {}
    postsInfo = {}
    for ( tid, thread ) in threads.iteritems():
      counts[ tid ] = {}
      threadsInfo[ tid ] = []
      for snapshot in thread[ THREAD_SNAPSHOTS ]:
        pid  = snapshot[ THREAD_SNAPSHOT_POSTID ]
        names = set( snapshot[ THREAD_SNAPSHOT_USER_RECENT_ACTIVITY ].keys() )
        history = snapshot[ THREAD_SNAPSHOT_POST_HISTORY ]
        # update referenced posts' child counts
        # add a child to most recent post by name for each name referenced
        post = posts[ pid ]
        username = post[ self.userCol ]
        names_matched[ pid ] = matchNamesInSet( post[ self.textCol ],\
                                  names.difference( [ username ] ) )
        for name in names_matched[ pid ]:
          mostrecent = snapshot[ THREAD_SNAPSHOT_USER_RECENT_ACTIVITY ][ name ]
          counts[ tid ][ mostrecent ] = counts[ tid ].get(mostrecent,0) + 1
  
        # update parent post's child counts
        aid = post[ self.aidCol ]
        postInfo = Post( pid, post[ self.textCol ], 
                         post[ self.timeCol ], post[ self.groupCol ])
        if not aid:
          # treat this post as a child of the preceeding post in thread
          try:
            aid = history[ -1 ]
          except:
            # this is the first post of the thread!
            threadsInfo[ tid ].append( postInfo )
            postsInfo[ pid ] = postInfo
            continue
        # add this Post as a child to the appropriate parent
        if aid in postsInfo.keys():
          postsInfo[ aid ].add_child( postInfo )
        else:
          #something went wrong, this post's ancestor is no longer here!
          print "Post ID {0} missing! Thread info: {1}".format( aid,
                                            post[ self.permalinkCol ] )
          threadsInfo[ tid ].append( postInfo )
        postsInfo[ pid ] = postInfo
        
    return threadsInfo

  def loadForum( self, fname ):
    """Method to read in the forum"""
    return self.recoverStructure( *self.loadCorpus( fname ) )

class CourseraParser( ForumParser ):
  self.headerrows   = 1
  self.idCol        = 0
  self.aidCol       = 1
  self.threadCol    = 2
  self.userCol      = 3
  self.groupCol     = 4
  self.timeCol      = 5
  self.textCol      = 6
  self.permalinkCol = 10

  def fixIDErrors( self, line, posts, openPID, openCID ):
    """
    void method to enforce metadata sanity
    """
    if line[ idCol ] == '' or line[ idCol ] == line[ aidCol ]:
      if line[ aidCol ] == '':
        line[ idCol ] = "post-x" + str( openPID )
        openPID = openPID + 1
      else:
        line[ idCol ] = "comment-x" + str( openCID )
        openCID = openCID + 1  
    return openPID, openCID

class EdXParser(ForumParser):
  headerrows   = 1
  idCol        = 0
  aidCol       = 1
  threadCol    = 2
  userCol      = 3
  groupCol     = 4
  timeCol      = 5
  textCol      = 6
  permalinkCol = 10
  pass
