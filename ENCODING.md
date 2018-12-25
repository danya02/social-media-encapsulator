# Encoding standards v.0.0.7

## Text
The data is encoded using Base64 encoding.
The text contains `[id]:[part-number]:[last-part-number]:[base64-encoded-data]`.
Any whitespace symbols are to be ignored.
This text format can be encoded into a medium other than text, such as QR-codes; however, the image encoding (below) should be considered first.

## Images
Pixels are to be read sequentially from left to right, and vertically downwards, i. e. normal western text reading order.

There are two ways of encoding data: either as black-and-white binary, or as a limited color palette.
Which of these two methods is used is dependent on the transmission medium: some may mangle colors so much that the red, green and blue data gets mixed, giving invalid results (in which case a binary encoding is necessary), while some may preserve enough information for the colored one to work.


If the data is black-and-white, each pixel is to be read as 1 bit of data: if the average color value is greater than 127, it's a 1; otherwise, it's a 0.
If it is colored, it can contain one of 8 colors. Each color corresponds to three bits (a one if the channel value is greater than 127, a zero otherwise, for red-green-blue in that sequence), offering a threefold increase in data capacity.

| Color | Conditions | Binary value |
| :----  | :----- | :-----|
| Blac**K**  | r<127, g<127, b<127 | `000` |
| **B**lue | r<127, g<127, b>127 | `001` |
| **G**reen | r<127, g>127, b<127 | `010` |
| **L**ight-blue | r<127, g>127, b>127 | `011` |
| **R**ed  | r>127, g<127, b<127 | `100` |
| **M**agenta | r>127, g<127, b>127 | `101` |
| **Y**ellow  | r>127, g>127, b<127 | `110` |
| **W**hite | r>127, g>127, b>127 | `111` |

The final pixel may contain more color information than the length of the message; in those cases, the tail bits are trimmed off.
For example, if the length of the message is 8, both `RYR` and `RYM` decode to `10011010`.

--------

The first 5 lines contain metadata and must not be used for the composition of the binary file.

Numbers are encoded in a big-endian format, padded with zeros.
Thus, for a field with a length of 32 bits, the number 78 should be encoded as follows: `00000000000000000000000001001110`.

The first line must indicate the object ID.
The ID must be unique to this object, or at least as unique as possible.

The next two lines indicate this piece's number: the first line the number of this piece (from 1 upwards), and the second line the number of the last piece.

The following 2 lines indicate this piece's length, in bits.
The number is to be broken across 2 lines; thus, if this piece is 69 bytes long and has a width of 10 pixels, then the values will be:

`0000000000`

`0001000101`


The rest of the file contains the actual data for this piece, wrapped at line length.



## Videos

A video is regarded as a series of frames.
Each frame is a QR-code.
Each QR code has to contain a string of this message's ID, this video's part number, the overall part number, this frame's number, the total number of frames, and the actual data piece (first gzip-ed, then Base64-coded), all separated by colons (":", ASCII 58 or 0x3a).
The reason each frame includes its own number in a movie is to avoid transposition errors, as well as to allow frames to be duplicated (for transmission through channels known to truncate videos).
