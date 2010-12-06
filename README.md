Description
===========


You'll find here all the open-source code I produce. This is just a collection of tiny utility scripts, patches, hacks and forks I want to or have to redistribute with the open source community at large.

If for any reason one of these hacks get momentum, I'll move them to a stand-alone and dedicated project.



Project list
============


adsl-monitoring
---------------

  Used with cron, this script help me to keep my broadband access alive.


audio-file-normalizer
---------------------

  This script parse a .m3u playlist file and convert Ogg/Vorbis and Flac files to AAC.


avi2mp4
-------

  This script convert avi files within the folder to compressed mp4/mp3 movies. Codecs parameters are adapted for tiny films taken with my cheap camera.


confsaver
---------

  A little python script to save a collection of files and directories into a bzip2 compressed archive.


crop-tiff-images
----------------

  This script crop big tiff files in the folder one by one. I wrote this script as a stupid but working workaround because ImageMagick can’t handle too many files at once (at least on my Mandriva 2005, it always crash after several files processed).


drupify-fork
------------

  This is a fork of the Drupify theme for Drupal 6.x. It holds all the modifications and hacks I added for Cool Cavemen's online shop (http://shop.coolcavemen.com).


findDuplicates
--------------

  This script use md5sum to track duplicate files in a folder.


KnewstickerToAkregator
----------------------

  This script parse the KNewsTicker configuration file of the current logged user to extract feeds references. Then the script generate a OPML/XML file that can be imported to Akregator.


KopeteChatRenderer
------------------

  This little script transform a Kopete history XML file to an ascii file. I’ve written this script to be able to copy and paste my chat with pals in e-mails.


la-bas.org-archive-download
---------------------------

  Similar to the previous script but designed to download Ogg archives of a french radio show thanks to wget.


maildir++2kmail
---------------

  This script import a Maildir++ ( http://en.wikipedia.org/wiki/Maildir#Maildir.2B.2B ) directory and its subfolders to Kmail.


maildir-deduplicate
-------------------

  This script compare all mails in a maildir folder and subfolders, then delete duplicate mails.
  You can give a list of mail headers to ignore when comparing mails between each others.
  I used this script to clean up a messed maildir folder after I move several mails from a Lotus Notes database.


mldonkey-auto-download
----------------------

  Combined with a cron entry, this script scan a given folder and auto start downloading torrent files found in that folder. Based on mldonkey and wget.


monthly-internet-uptime
-----------------------

  This script help me to monitor how long my backup Dial-up modem is up per month.


osdir-slideshow
---------------

  I wrote this script to get a series of screenshots from well-known OSdir slideshows.


phorum_anon2user
----------------

  This is a little script I wrote for Phorum, to give a owner to anonymous post.


phorum_bodies_update
--------------------

  Script to convert old message format to new format (with the conversion of html tags to Phorum specific tags).


phorum_to_e107
--------------

  This script is designed to migrate Phorum 3.x ( http://www.phorum.org ) datas to a new empty e107 website. The destination e107 platform must be empty because this script copy Phorum id and don’t re-index database records.


process-monitoring
------------------

  This script, combined with cron, help me to keep an eye on a running process.


system-backup
-------------

  This script automate system backups thanks to rdiff-backup and rsync. It is based on an idea from the “Backup up on unreliable link” article ( http://wiki.rdiff-backup.org/wiki/index.php/BackupUpOnUnreliableLink ) from the official rdiff-backup wiki ( http://wiki.rdiff-backup.org ).


website-backup
--------------

  This script automate the mirroring of several external websites (both files and MySQL databases) thanks to lftp, mysqldump, ssh and rsync. Then it make an incremental backup each day thanks to rdiff-backup and finally a snapshot each month.


xwd2png
-------

  This script convert .xwd images taken with xvidcap to a series of .png images. I wrote this because mencoder can’t read xwd files.



Legals
======


Licence
-------

  Unless otherwise noted, code in this repository is distributed under a GNU GPL2+ licence.


Disclaimer
----------

  All the code here is provided as is and with no guarentee - back up your data first, I am not responsible for anything bad that happens to you as a result of using my hacks.


Author
------

  Kevin Deldycke. Find me at http://kevin.deldycke.com .

