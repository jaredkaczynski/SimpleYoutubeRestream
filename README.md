# SimpleYoutubeRestream
Simple restreamer for Youtube. Takes in an HLS stream and outputs it to Youtube using FFMPEG. Has a backup stream of a static image that runs when the main stream dies to allow for constant Youtube streaming events. 


Usage:

Create an image for the error case called error.png of size outputstreamresolution.

Then, restream.py url.m3u8 youtubekey

Upon start it checks if the stream is available. If it is, it starts the stream then verifies every few seconds it still is live. On death the ffmpeg instance is killed and static streaming starts. Every few seconds the stream is checked if alive, once alive, static is killed and main stream goes up again. This avoids the issue of dead Youtube streams.
