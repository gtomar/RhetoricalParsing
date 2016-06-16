import ast, os
import pygeoip, sys
from datetime import tzinfo, timedelta
import datetime
import csv
import pickle

######## USER PARAMETERS ########
inputdir  = '/media/maki/OS/Users/Keith/Documents/CMU/Research/Nanotech/MOOC2/CLICKSTREAM DATA/data1/nanosar-001_clickstream_export/'
filename  = 'nanosar-001_clickstream_export'
forumdir  = '/media/maki/OS/Users/Keith/Documents/CMU/Research/Nanotech/MOOC2/ExtractedCSVs/'
forumfile = 'anonymized_forum_posts_pid_tid_uid_deleted_anonymous_votes_text_timestamp.csv'
numHeaderRows = 1 # The number of header rows in the forum dump spreadsheet
IDcol         = 2 # The column in the forum dump spreadsheet containing userID    information
dataCol       = 7 # The column in the forum dump spreadsheet containing timestamp information
outdir      = '/media/maki/OS/Users/Keith/Documents/CMU/Research/Nanotech/MOOC2/'
geolitecity = '/home/maki/Downloads/GeoLiteCity.dat'
# This could be encoded more elegantly...
startweek   = 10
###### END USER PARAMETERS ######

# Used in in converting IP addresses to cities
gi = pygeoip.GeoIP(geolitecity)

# Used in converting timestamps to UTC
class UTC(tzinfo):
  """UTC"""
  def utcoffset(self, dt):
    return timedelta(0)
  def tzname(self, dt):
    return "UTC"
  def dst(self, dt):
    return timedelta(0)

entries = []
errors  = 0
f = open(os.path.join(inputdir,filename),'rb')
for l in f:
  try:
    entries.append(ast.literal_eval(l[:-1]))
  except SyntaxError,e:
    print e
    errors = errors + 1

studentclicks   = {}
studentposts    = {}
studentIPs      = {}
drops           = {}
joins           = {}
students        = set()
problemstudents = {}
for entry in entries:
  if not len(entry['username'])==len(entries[0]['username']):
    print len(entry['username'])
  clicktime = datetime.datetime.fromtimestamp(float(entry['timestamp'])/1000,UTC())
  week = (datetime.date(clicktime.year,clicktime.month,\
	               clicktime.day).isocalendar()[1] - startweek)%52 + 1
  if week==52:
    continue # These clicks were from the instructors pre-launch
  if week not in studentclicks.keys():
    # First click of the week!
    studentclicks[week]   = {}
    studentIPs[week]      = {}
    problemstudents[week] = set()

  # Update join/drop weeks for this student if necessary
  drops[entry['username']] = max(drops.setdefault(entry['username'],week),week)
  joins[entry['username']] = min(joins.setdefault(entry['username'],week),week)

  if entry['username'] in studentclicks[week].keys():
    # Update counts for this week
    studentclicks[week][entry['username']] = \
          studentclicks[week][entry['username']] + 1
  else:
    # New student activity this week!
    studentclicks[week][entry['username']] = 1
    try:
      studentIPs[week][entry['username']] = \
           gi.record_by_addr(entry['user_ip'])['country_name']
    except:
      ips = entry['user_ip'].split()
      try: 
        studentIPs[week][entry['username']] = \
             gi.record_by_addr(ips[0])['country_name']
        print "Two IPs found for student.  IP1: " + gi.record_by_addr(ips[0])['country_name'] +\
                                         " IP2: " + gi.record_by_addr(ips[1])['country_name']
      except:
        #print "IP address could not be decoded!  IP: " + entry['username']
        problemstudents[week].update([entry['username']])
    students.update([entry['username']])

print "The following student weeks could not be identified:"
for week in problemstudents.keys():
  for student in problemstudents[week]:
    print student + " " + str(week)

# Open CSV file
worksheet = csv.reader( open( forumdir + forumfile, 'rb' ) )
IDs = []
dataVals = []

# Read in the data ignoring header rows
for x in range(numHeaderRows):
  print worksheet.next() # Throw away header lines
numskipped = 0
for line in worksheet:
  posttime = datetime.datetime.fromtimestamp(float(line[dataCol])/1000,UTC())
  week = (datetime.date(posttime.year, posttime.month,\
	                posttime.day).isocalendar()[1] - startweek)%52 + 1
  if week==52 or week==51:
    numskipped = numskipped + 1
    continue # These posts were from the instructors pre-launch
  if week not in studentposts.keys():
    # First post of the week!
    studentposts[week]  = {}

  # Update join/drop weeks for this student if necessary
  drops[line[IDcol]] = max(drops.setdefault(line[IDcol],week),week)
  joins[line[IDcol]] = min(joins.setdefault(line[IDcol],week),week)

  if line[IDcol] in studentposts[week].keys():
    # Update counts for this week
    studentposts[week][line[IDcol]] = studentposts[week][line[IDcol]] + 1
  else:
    # New student activity this week!
    studentposts[week][line[IDcol]] = 1
    students.update([entry['username']])
if numskipped > 0:
  print numskipped + " posts were timestamped before the course start week."

fw = csv.writer(open(os.path.join(outdir,'survivaltable.csv'),'wb'))
for student in students:
  for week in range(joins[student],drops[student]):
    if week in studentclicks.keys() and student in studentclicks[week].keys():
      clicks = studentclicks[week][student]  
    else:
      clicks = 0
    if week in studentposts.keys() and student in studentposts[week].keys():
      posts  = studentposts[week][student]    
    else:
      posts  = 0
    if week in studentIPs.keys() and student in studentIPs[week].keys():
      fw.writerow([student, week, (1+week-joins[student]), studentIPs[week][student], clicks, posts, "false"])
    else:
      fw.writerow([student, week, (1+week-joins[student]), "Unknown", clicks, posts, "false"])    
  if drops[student] in studentclicks.keys() and student in studentclicks[drops[student]].keys():
    clicks = studentclicks[drops[student]][student]
  else:
    clicks = 0
  if drops[student] in studentposts.keys() and student in studentposts[drops[student]].keys():
    posts  = studentposts[drops[student]][student]   
  else:
    posts  = 0
  if drops[student] in studentIPs.keys() and student in studentIPs[drops[student]].keys():
    fw.writerow([student, drops[student], (1+drops[student]-joins[student]), studentIPs[drops[student]][student], clicks, posts, "true"])
  else:
    fw.writerow([student, drops[student], (1+drops[student]-joins[student]), "Unknown", clicks, posts, "true"])

populations = {}
for student in students:
  lifetime = 1+drops[student]-joins[student]
  populations[lifetime] = populations.setdefault(lifetime,0)+1
print populations

IPcounts = {}
countryMap = {}
movers = []
for student in students:
  hasCountry = False
  Country = ""
  for week in range(joins[student],drops[student]+1):
    if week in studentIPs.keys() and student in studentIPs[week].keys():
      hasCountry = True
      Country = studentIPs[week][student]
      if student in countryMap.keys() and not Country == countryMap[student] and not Country=='Unknown':
        movers.append(student)
      if student not in countryMap.keys() or not Country=='Unknown':
        countryMap[student] = Country
  if hasCountry:
    IPcounts[Country] = IPcounts.setdefault(Country,0)+1
print IPcounts
print len(students) - sum([v for v in IPcounts.values()])

pickle.dump(countryMap, open('/media/maki/OS/Users/Keith/Documents/CMU/Research/Nanotech/MOOC2/ExtractedCSVs/Student_FinalIPCountryInfo.pickle','wb'))

