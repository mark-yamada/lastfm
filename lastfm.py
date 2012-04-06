#Create a tiled image from a user's top albums on last.fm
# Mark Yamada 2012


import urllib
import urllib2
import sys
import string
import math
import argparse
from PIL import Image
from PIL import _imaging
from xml.dom import minidom
import random

#Determine ideal tile size from resolution and the number of covers.
def get_tileSize (width, height, numImages):
	area = width * height
	imageArea = float(area) / numImages
	optImageDim = math.sqrt(imageArea)

  #Opt for no extra vertical space.
	numVertImages = math.floor(height / optImageDim)
	return int(math.ceil(height / numVertImages))
	
#Some defaults

parser = argparse.ArgumentParser(description='Create a tiled collage from a last.fm user\'s top albums.')
parser.add_argument('oFile', metavar='output_file', type=argparse.FileType('w'), default='lastfm.png')
parser.add_argument('--verbose', '-v', dest='verbose', action='store_const', default=False, const=True)
parser.add_argument('--height', '-H', dest='height', type=int, default=600)
parser.add_argument('--width', '-W', dest='width', type=int, default=800)
parser.add_argument('--coverLimit', '-l', dest='coverLimit', type=int, default=100)
parser.add_argument('--user', '-u', dest='user', metavar='USERNAME', type=str, required=True) 
parser.add_argument('--period', '-p', dest='period', type=str, choices=('overall', '7day', '3month', '6month', '12month'), default='overall') 

args = parser.parse_args()

api_key = '73ad19e9a1a9244e283ce7f1ae90b7dc'
pathStr='/topalbums/album/name[1]'

#Get XML for top album URLs
topAlbumsXML = urllib2.urlopen(str.format('http://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user={0}&api_key={1}&period={2}&limit={3}', args.user, api_key, args.period, args.coverLimit))
parsedAlbums = minidom.parse(topAlbumsXML)
albumImages = parsedAlbums.getElementsByTagName('image')

#Pull the images urls out and shuffle them.
urlList= [imageURL.firstChild.data for imageURL in albumImages if imageURL.attributes['size'].value == 'extralarge' and '/noimage/' not in imageURL.firstChild.data]
random.shuffle(urlList)
numImages = len(urlList)

tileSize = get_tileSize (args.width, args.height, numImages)
extraHorizSpace = args.width % tileSize #per row

#make canvas
wp = Image.new('RGB', (args.width, args.height))
x = 0
y = 0

print 'Found %d covers for %s with period=%s' % (numImages, args.user, args.period)

toggle = False

for imgUrl in urlList:
	if args.verbose:
		print 'Getting ' + imgUrl 

	try:
		coverImage = Image.open(urllib.urlretrieve(imgUrl)[0])
		coverImage = coverImage.resize((tileSize,tileSize), Image.ANTIALIAS)
	except Exception as e:
		print 'Could not open ' + imgUrl
		print e
		# Should fix this to just make it resize
		sys.exit() 
		continue
	
	wp.paste(coverImage,(x,y))
	x = x + tileSize
	if x >= args.width:
		if toggle:
			x = 0
		else:
			x = -(tileSize - extraHorizSpace)
		toggle = not toggle
		y = y + tileSize
	
	if y >= args.height:
		break

wp.save(args.oFile)
print "Wrote image file to %s." % args.oFile.name
