LyricDownloader
===============

A lyric downloader implemented in Python 3

##Usage
###Download the plain lyric
	lrc = LyricDownloader()
	print lrc.get_plain(artist, title)

###Download the .lrc file
	lrc = LyricDownloader()
	print lrc.get_lrc(artist, title)

##Notice
This program uses the API from Qianqian.com. There is a chance that you get `None`, which simply means the request fails. You can try it later.
