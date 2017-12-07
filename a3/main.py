# Image compression
#
# You'll need Python 2.7 and must install these packages:
#
#   scipy, numpy
#
# You can run this *only* on PNM images, which the netpbm library is used for.
#
# You can also display a PNM image using the netpbm library as, for example:
#
#   python netpbm.py images/cortex.pnm


import sys, os, math, time, netpbm,struct
import numpy as np


# Text at the beginning of the compressed file, to identify it


headerText = 'my compressed image - v1.0'

# Compress an image


def compress( inputFile, outputFile ):

  # Read the input file into a numpy array of 8-bit values
  #
  # The img.shape is a 3-type with rows,columns,channels, where
  # channels is the number of component in each pixel.  The img.dtype
  # is 'uint8', meaning that each component is an 8-bit unsigned
  # integer.

  img = netpbm.imread( inputFile ).astype('uint8')
  
  # Compress the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO FILL THE 'outputBytes' ARRAY.
  #
  # Note that single-channel images will have a 'shape' with only two
  # components: the y dimensions and the x dimension.  So you will
  # have to detect this and set the number of channels accordingly.
  # Furthermore, single-channel images must be indexed as img[y,x]
  # instead of img[y,x,1].  You'll need two pieces of similar code:
  # one piece for the single-channel case and one piece for the
  # multi-channel case.

  startTime = time.time()

  dimensions = len(img.shape)

  # if single channel
  if dimensions == 2:

    # Empty dictionary
    d = {}
    # Current dictionary index
    dict_index = 0
    # Previous value
    prev = 0

    for i in range(-255, 256):
      # Stores the binary value
      d[(struct.pack('>h',i))]=i+255
      dict_index = i + 255


    outputBytes = bytearray()
      # p is the byte pattern that will be passed into the dictionary
    p = ""
    p_c = ""

    for y in range(img.shape[0]):
      for x in range(img.shape[1]):

        # c is the current byte being analyzed
        c = int(img[y][x])-int(prev)
        prev=img[y][x]

        bc= struct.pack('>h', c)
        p_c = p + bc

          # if the character c is already in the dictionary add it to the present character stream
        if p_c in d:
          p = p_c
        else:
          val = struct.pack('>H', d[p])
          b1, b2 = struct.unpack('>BB', val)
          outputBytes.append(b1)
          outputBytes.append(b2)
          if dict_index<65535:
            dict_index += 1
            d[p_c] = dict_index
          p = bc
    outputFile.write('%d %d\n' % (img.shape[0], img.shape[1]))
    outputBytes.append(img[y, x])


  # if multichannel
  elif dimensions > 2:

    # Empty dictionary
    d = {}
    # Current dictionary index
    dict_index = 0

    # Previous values
    prev = []

    for i in range(img.shape[2]):
      prev.append(0)

    for i in range(-255, 256):
      # Stores the binary value
      d[(struct.pack('>h', i))] = i + 255
      dict_index = i + 255

    outputBytes = bytearray()
    # p is the byte pattern that will be passed into the dictionary
    p = ""
    p_c = ""

    for y in range(img.shape[0]):
      for x in range(img.shape[1]):
        for channel in range(img.shape[2]):

          # c is the current byte being analyzed
          c = int(img[y][x][channel]) - int(prev[channel])
          prev[channel] = img[y][x][channel]

          bc = struct.pack('>h', c)
          p_c = p + bc

          # if the character c is already in the dictionary add it to the present character stream
          if p_c in d:
            p = p_c
          else:
            val = struct.pack('>H', d[p])
            b1, b2 = struct.unpack('>BB', val)
            outputBytes.append(b1)
            outputBytes.append(b2)
            if dict_index < 65535:
              dict_index += 1
              d[p_c] = dict_index
            p = bc
    outputFile.write('%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2]))
    outputBytes.append(img[y, x, channel])

  # Output the bytes
  #
  # Include the 'headerText' to identify the type of file.  Include
  # the rows, columns, channels so that the image shape can be
  # reconstructed.

  outputFile.write('%s\n' % headerText)
  outputFile.write(outputBytes)

  # Print information about the compression
  inSize = img.shape[0] * img.shape[1]

  outSize = len(outputBytes)
  

  endTime = time.time()

  sys.stderr.write( 'Input size:         %d bytes\n' % inSize )
  sys.stderr.write( 'Output size:        %d bytes\n' % outSize )
  sys.stderr.write( 'Compression factor: %.2f\n' % (inSize/float(outSize)) )
  sys.stderr.write( 'Compression time:   %.2f seconds\n' % (endTime - startTime) )
  


# Uncompress an image

def uncompress( inputFile, outputFile ):

  # Check that it's a known file

  if inputFile.readline() != headerText + '\n':
    sys.stderr.write( "Input is not in the '%s' format.\n" % headerText )
    sys.exit(1)
    
  # Read the rows, columns, and channels.  

  rows, columns, channels = [ int(x) for x in inputFile.readline().split() ]

  # Read the raw bytes.

  inputBytes = bytearray(inputFile.read())

  # Build the image
  #
  # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes' ARRAY INTO AN IMAGE IN 'img'.

  startTime = time.time()

  img = np.empty( [rows,columns,channels], dtype=np.uint8 )

  byteIter = iter(inputBytes)
  for y in range(rows):
    for x in range(columns):
      for c in range(channels):
        img[y,x,c] = byteIter.next()

  endTime = time.time()

  # Output the image

  netpbm.imsave( outputFile, img )

  sys.stderr.write( 'Uncompression time: %.2f seconds\n' % (endTime - startTime) )

  

  
# The command line is 
#
#   main.py {flag} {input image filename} {output image filename}
#
# where {flag} is one of 'c' or 'u' for compress or uncompress and
# either filename can be '-' for standard input or standard output.


if len(sys.argv) < 4:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)

# Get input file
 
if sys.argv[2] == '-':
  inputFile = sys.stdin
else:
  try:
    inputFile = open( sys.argv[2], 'rb' )
  except:
    sys.stderr.write( "Could not open input file '%s'.\n" % sys.argv[2] )
    sys.exit(1)

# Get output file

if sys.argv[3] == '-':
  outputFile = sys.stdout
else:
  try:
    outputFile = open( sys.argv[3], 'wb' )
  except:
    sys.stderr.write( "Could not open output file '%s'.\n" % sys.argv[3] )
    sys.exit(1)

# Run the algorithm

if sys.argv[1] == 'c':
  compress( inputFile, outputFile )
elif sys.argv[1] == 'u':
  uncompress( inputFile, outputFile )
else:
  sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
  sys.exit(1)

