# social-media-encapsulator
Use social media websites to move BLOBs.

Some ISPs provide data plans (for example, [this one](http://www.mts.ru/mob_connect/tariffs/tariffs/hype/)) that have a limit on data traffic, but certain sites are exempted from that limit.
Most often, those are social media sites.
Now, despite the highly dubious marketing of these plans, they may be useful to people who use these social media sites often enough.
It has to be noted, however, that they support pictures, videos, audios and texts and often have an easy-to-use API.

Hmm...

-----

Apart from the dependencies listed in requirements.txt, this also needs [ZBar](http://zbar.sourceforge.net/download.html) to be installed, or an equivalent program that is called `zbarimg`, takes an argument list of `--raw` and an arbitrary number of image files, and prints out the data encoded in the QR codes.
