# Encoding description v.0.0.1
## Images
Pixels are to be read sequentially from left to right, and vertically downwards, i. e. normal human reading order.
Each pixel is to be read as 3 bytes of information: the red byte, the green byte and the blue byte.
The alpha channel must be ignored, as that information is most often lost.

The first line contains metadata and must not be used for the composition of the binary file.

The first 8 pixels (24 bytes) must indicate the object ID.
The ID must be unique to this object, or at least as unique as possible.
One possible composition of this field is 1.5 [UUIDs](https://en.wikipedia.org/wiki/Universally_unique_identifier).

The following 8 pixels must indicate this piece's number: the first 4 pixels the number of this part, the next 4 pixels the total number of parts.
The first piece should be number 1.
The number must be stored in a big-endian format.

For example, if the number field's value is `00` `00` `00` `00` `00` `00` `00` `00` `be` `ef` `de` `ad` `00` `00` `00` `00` `00` `00` `00` `00` `de` `ad` `be` `ef`,
then this is part 3203391149 of 3735928559.

The rest of this line is undefined.
Use it in any way you may deem useful.