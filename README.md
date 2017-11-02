# social-media-encapsulator
Use social media websites to move BLOBs.

Some ISPs provide data plans (for example, [this one](http://www.mts.ru/mob_connect/tariffs/tariffs/hype/)) that have a limit on data traffic, but certain sites are exempted from that limit.
Most often, those are social media sites.
Now, despite the highly dubious marketing of these plans, they may be useful to people who use these social media sites often enough.
It has to be noted, however, that they support pictures, videos, audios and texts and often have an easy-to-use API.

Hmm...

2 November 2017: The original idea has proven to be a bust.
It would appear as if major social media encode their pictures in JPG, which is a lossy format, and discard the lossless originals.
Since this program depends on losslessness of the pictures, that wouldn't work.