#![preview thumb](https://github.com/rembo10/headphones/raw/master/data/images/headphoneslogo.png)Headphones

###Notes
This is a fork of performance branch of majello/headphones, which seems to have varios problems and not being updated

What is done here:
* dynamic loading of database adapters

What is broken:
* pretty much everything concerning databases other than sqlite

What is planned:
* fix what's broken :)
* add ElasticSearch support
* to have performance optimised and pythonized version of Headphones


This is a fork of Headphones by rembo10. I intend to provide database connectivity beyond sqlite and various optimizations, improvements.
The current version adds:
* mySQL connectivity
* Export to CSV for mySQL and sqllite
* migration between sqllite and mysql
* database check and clean for sqllite
* progress display for long running/background jobs
* artist management functions (e.g. pause resume artists with no last album etc.)
* optional fast database update for large libaries
* various performance tweaks

Next on the list:
* expand DB schema to include founded and dissolved information
* add management functions to take advantage of this information
* change manageArtists to allow filtering by automanage options

Long term plans:
* include tracks from the library that are currently not shown (don't always rely on musicbrainz)
* include spydaap to share with itunes (maybe, spydaap will need updates to work with current iTunes)

###Installation and Notes

This is a relatively early release of a third-party add-on for SABnzbd. It's been around for about a year, and while
quite functional, there are still a lot of kinks to work out!

To run it, just double-click the Headphones.py file (in Windows - you may need to right click and click 'Open With' -> Python) or launch a terminal, cd into the Headphones directory and run 'python headphones.py'.

For additional startup options, type 'python Headphones.py -h' or 'python Headphones.py --help'

###Screenshots

Homepage (Artist Overview)

![preview thumb](http://i.imgur.com/LZO9a.png)

One of the many settings pages....

![preview thumb](http://i.imgur.com/xcWNy.png)

It might even know you better than you know yourself:

![preview thumb](http://i.imgur.com/R7J0f.png)

Import Your Favorite Artists:

![preview thumb](http://i.imgur.com/6tZoC.png)

Artist Search Results (also search by album!):

![preview thumb](http://i.imgur.com/rIV0P.png)

Artist Page with Bio & Album Overview:

![preview thumb](http://i.imgur.com/SSil1.png)

Album Page with track overview:

![preview thumb](http://i.imgur.com/kcjES.png)

If you run into any issues, visit http://headphones.codeshy.com/forum and report an issue. 

This is free software under the GPL v3 open source license - so feel free to do with it what you wish.
