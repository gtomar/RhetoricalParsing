import math
from memo import *

class ParseError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class ParseTree(object):
  """
  Class for rhetorical structure tree parses
  """
  def __init__(self, unit, relation, start, end, text=None, children=None, parent=None):
    self.unit     = unit
    self.relation = relation 
    self.start    = start
    self.end      = end
    self.text     = text
    self.children = children
    self.parent   = parent

  def isLeaf(self):
    return self.children is None

  def isRoot(self):
    return self.parent is None

  def getChildren(self):
    return self.children
 
  def getParent(self):
    return self.parent

  def getUnit(self):
    return self.unit

  def isDummy(self):
    return self.isRoot() and not self.isLeaf() \
       and len(self.getChildren()) == 1 \
       and self.getChildren()[0].getUnit() == "DUMMY"

  def getRelation(self):
    return self.relation

  def getStart(self):
    return self.start

  def getEnd(self):
    return self.end

  def getText(self):
    return self.text

  def assignParentsToChildren(self):
    if not self.isLeaf():
      for child in self.getChildren():
        child.assignParentsToChildren()
        child.parent = self

  def postOrderRelations(self,node):
    if node.isLeaf():
      return [node.getRelation()] # No children, only self's relation
    else:
      subrel = [rel for child in node.getChildren() for rel in node.postOrderRelations(child)]
    if node.isRoot():
      return subrel # No relation for self, only relations of children
    else:
      return subrel+[node.getRelation()] # Proper post order traversal

  def extractTraversalFeatures(self):
    self.assignParentsToChildren()
    return ["".join([str(el) for el in feature]) for feature in \
            [self.extractInOrderUnit(),self.extractInOrderDepth(),\
             self.extractLeafUnit(),self.extractLeafDepth(),\
             self.extractInOrderRelations(1),self.extractInOrderRelations(2),\
             self.extractInOrderRelations(-1)]]

  def extractInOrderUnit(self):
    if self.isDummy():
      return ["DUMMY"]
    if self.isLeaf():
      return [self.getUnit()]
    return self.getChildren()[0].extractInOrderUnit()+\
          [self.getUnit()]+\
           self.getChildren()[1].extractInOrderUnit()

  def extractInOrderDepth(self):
    if self.isDummy() or self.isLeaf():
      return [0]
    return [1+el for el in self.getChildren()[0].extractInOrderDepth()]+\
           [0]+\
           [1+el for el in self.getChildren()[1].extractInOrderDepth()]

  def extractLeafUnit(self):
    if self.isDummy():
      return ["DUMMY"]
    if self.isLeaf():
      return [self.getUnit()]
    return self.getChildren()[0].extractInOrderUnit()+\
           self.getChildren()[1].extractInOrderUnit()

  def extractLeafDepth(self):
    if self.isDummy() or self.isLeaf():
      return [0]
    return [1+el for el in self.getChildren()[0].extractLeafDepth()]+\
           [1+el for el in self.getChildren()[1].extractLeafDepth()]

  def extract1Level(self):
    if self.isDummy() or self.isLeaf():
      return self.getNullPrint(1)
    return [child.getRelation() for child in self.getChildren()]

  def extract2Level(self):
    if self.isDummy() or self.isLeaf():
      return self.getNullPrint(2)
    rels = [el for child in self.getChildren() for el in child.extract1Level()]
    childrels = [child.getRelation() for child in self.getChildren()]
    return 

  def extractInOrderRelations(self,level=-1):
    if self.isDummy():
      ourRelation = "DUMMY"
    elif self.isRoot():
      ourRelation = "Root"
    else:
      ourRelation = self.getRelation()
    if self.isLeaf() or self.isDummy() or level==0:
      return self.getNullPrint(level)+\
             [ourRelation]+\
             self.getNullPrint(level)
    return self.getChildren()[0].extractInOrderRelations(level-1)+\
           [ourRelation]+\
           self.getChildren()[1].extractInOrderRelations(level-1)

  def getNullPrint(self,level):
    if level>0:
      return int(math.pow(2,level)-1)*["Null"]
    else:
      return []

  def localRelationFeatures(self):
    return None

  def toString(self):
    if self.isLeaf():
      return self.getText()
    else:
      return " ".join([child.toString() for child in  self.getChildren()])

  def toJSON(self):
    retval = {   "Start":self.start,
                   "End":self.end,
                  "Unit":self.unit,
                  "Text":self.text,
              "Relation":self.relation }
    if self.isLeaf():
      retval["Children"] = "None"
    else:
      retval["Children"] = []
      for child in self.getChildren():
        retval["Children"].append(child.toJSON())
    return retval
 
def fromJSON(treedict):
  if treedict["Children"] == "None":
    children = None
  else:
    children = []
    for child in treedict["Children"]:
      children.append(fromJSON(child))
  tree = ParseTree(treedict["Unit"],treedict["Relation"],
                   treedict["Start"],treedict["End"],
                   treedict["Text"],children=children)
  tree.assignParentsToChildren()
  return tree

def compressOutput(func):
  def compressed(param):
    return [output.toJSON() for output in func(param)]
  return compressed

def restoreOutput(func):
  def restored(param):
    return [fromJSON(output) for output in func(param)]
  return restored

# return type: list of type ParseTree (forest)
# Serializes the ParseTree as a dictionary to JSON
@restoreOutput
@memo_pickle_to_file("/usr0/home/gtomar/RSTForest.cache")
@compressOutput
def parseRSTForest(treestring):
  """parse Joty's monologue rhetorical parser treestring output"""
  forest = parseRSTTrees(treestring)[0]
  for tree in forest:
    tree.assignParentsToChildren()
  return forest

# return type: (forest, length of string consumed)
def parseRSTTrees(treestring):
  """parse Joty's monologue rhetorical parser treestring output"""
  forest = []
  ind = 0
  if len(treestring) == 0:
    raise ParseError("Error: Cannot parse the empty string!")
  if treestring[ind] == '(':
    blocks = treestring[ind+2:].split('(')[:3]
    endofblocks = sum([len(block) for block in blocks])
    # try to intelligently find text field
    if endofblocks < len(treestring):
      texts = treestring[endofblocks+5:].split("text _!")[1].split("_!) ")
      endind = endofblocks+11+len(texts[0])+len(texts[1].split('('))
      blocks.append("text _!" + "_!) ".join([texts[0],texts[1].split('(')[0]]))
    else:
      blocks.append(treestring[ind+2:].split('(')[3:4])
    header = blocks[0][:-1]
    span = blocks[1].strip()[:-1].split()
    relation = blocks[2].strip()[:-1].split()
    if header == 'Root':
      # parse our children
      ind = 4 + len(header) + len(blocks[1])
      if span[1]==span[2]:
        # we have one child
        child = parseRSTTrees(treestring[ind:])
        children = child[0] #this is a list with one el
        ind += child[1]
      else:
        # we have two children
        child1 = parseRSTTrees(treestring[ind:])
        child2 = parseRSTTrees(treestring[ind+child1[1]:])
        children = child1[0]+child2[0] # forest concatenation
        ind += child1[1] + child2[1]
      # add our parse to the forest
      forest.append(ParseTree(header,None,span[1],span[2],children=children))

    elif relation[0] == 'rel2par':
      # we are a subspan with a rhetorical relation
      if span[0] == 'leaf' and blocks[3][:4] == 'text':
        # we are in a leaf node        
        # get our text
        text = blocks[3].split("_!)")[0][7:].replace("\\\\\\\"","\"")
        # and add a leaf to our forest
        forest.append(ParseTree(header,relation[1],span[1],span[1],text=text))
        ind += 5+sum([len(block) for block in blocks])
        return (forest,ind)

      elif span[0] == 'span':
        # we have two children, parse each
        ind = 4 + len(blocks[0]) + len(blocks[1]) + len(blocks[2])
        child1 = parseRSTTrees(treestring[ind:])
        child2 = parseRSTTrees(treestring[ind+child1[1]:])
        children = child1[0]+child2[0] # forest concatenation
        ind += child1[1] + child2[1]
        # add our parse to the forest
        forest.append(ParseTree(header,relation[1],span[1],span[2],children=children))
        return (forest,ind)
      else:
        raise ParseError("Error: Input has invalid span type: {0}".format(treestring[:100]))
    else:
      raise ParseError("Error: Unexpected relation information in input: {0}".format(treestring[:100]))
    if ind < len(treestring):
      #we have more trees to parse
      subparse = parseRSTTrees(treestring[ind:])
      forest += subparse[0]
      ind += subparse[1]
    # error case-- we didn't parse everything!
    if ind < len(treestring):
      raise ParseError("Error: Failed to properly parse input: {0}".format(treestring[:100]))
    return (forest,ind)
  raise ParseError("Error: Input is not a valid parsetree: {0}".format(treestring[:100]))
