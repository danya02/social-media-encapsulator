# Encoding description v.0.0.3
## Images
Pixels are to be read sequentially from left to right, and vertically downwards, i. e. normal human reading order.
Each pixel is to be read as 1 bit of data: if the average color value is greater than 127, it's a 1; else, it's a 0.

The first 5 lines contain metadata and must not be used for the composition of the binary file.

Numbers are encoded in a big-endian format, padded with zeros.
Thus, for a field with a length of 32 bits, the number 78 should be encoded as follows: `00000000000000000000000001001110`.

The first line must indicate the object ID.
The ID must be unique to this object, or at least as unique as possible.

The next two lines indicate this piece's number: the first line the number of this piece (from 1 upwards), and the second line the number of the last piece.

The following 2 lines indicate this piece's length, in bytes.
The number is to be broken across 2 lines; thus, if this piece is 69 bytes long and has a width of 10 pixels, then the values will be:

`0000000000`

`0001000101`


The rest of the file contains the actual data for this piece, wrapped at line length.