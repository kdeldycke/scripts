Description
-----------

This repository is a collection of tiny utility scripts, patches and hacks.

These are mostly one-time scripts, very old and very specific. I doubt you'll be able to use them as-is. Until you update and tweak them to fit your needs. In this case, don't hesitate to send me code and patches.

The code here is generally poorly written. Either because my coding style has improved since I wrote them, or because I didn't bother to make the code elegant after I finished my first working iteration.

If for any reason one of these script get momentum, I'll consider moving it to a stand-alone and dedicated project.


Content
-------

*   adsl-monitoring.py

    Used with `cron`, this script help me to keep my unreliable broadband access alive.

*   audio-file-normalizer.py

    This script parse a `.m3u` playlist file and convert Ogg/Vorbis and Flac files to AAC.

*   avi2mp4.py

    This script convert Avi files within the folder to compressed MP4/MP3 movies. Codecs parameters are adapted for tiny films taken with my cheap camera. This is VLC-based but older version were based on mplayer/mencoder.

*   bbpress-to-mailbox.py



*   bbpress-to-wordpress.py



*   confsaver.py

    A little python script to save a collection of files and directories into a Bzip2 compressed archive.

*   cron-monitor-network.py



*   crop-tiff-images.py

    This script crop big tiff files in the folder one by one. I wrote this script as a stupid but working workaround to ImageMagick which wasn't able to handle too many files at once (at least on my Mandriva 2005, it always crash after several files processed).

*   findDuplicates.py

    This script search and display all duplicate files within a folder structure.

*   getAgentList.py



*   KnewstickerToAkregator.py

    This script parse the KNewsTicker configuration file of the current logged user to extract feeds references. Then the script generate a OPML/XML file that can be imported to [Akregator](http://akregator.kde.org/). Prerequisite: KNewsTicker and pyxml.

*   KopeteChatRenderer.py

    This little script transform a Kopete history XML file to an ASCII file. I’ve written this script to be able to copy and paste my chat with pals in e-mails.

*   la-bas.org-archive-download.py

    Similar script to `osdir-slideshow` but designed to download Ogg archives of a french radio show thanks to wget.

*   maildir2ical.py



*   maildir++2kmail.py

    This script import a [Maildir++](http://en.wikipedia.org/wiki/Maildir#Maildir.2B.2B) directory and its subfolders to [Kmail](http://kontact.kde.org/kmail).

*   mail_ingestor.py



*   mass-replace.py



*   mechanize-playground.py



*   mldonkey-auto-download.sh

    Combined with a cron entry, this script scan a given folder and auto start downloading torrent files found in that folder. Based on mldonkey and wget.

*   monthly-internet-uptime.py

    This script help me to monitor how long my backup Dial-up modem is up per month.

*   osdir-slideshow.py

    I wrote this script to get a series of screenshots from well-known OSdir slideshows.

*   phorum_anon2user.php

    This is a little script I wrote for Phorum, to give a owner to anonymous post.

*   phorum_bodies_update.php

    Script to convert old message format to new format (with the conversion of HTML tags to Phorum specific tags).

*   phorum_to_e107.php

    This script is designed to migrate [Phorum 3.x](http://www.phorum.org) datas to a new empty e107 website. The destination e107 platform must be empty because this script copy Phorum id and don’t re-index database records.

*   phorum-to-wordpress.py



*   process-monitoring.py

    This script, combined with cron, help me to keep an eye on a running process.

*   qlc-effects-generator.py



*   svn2ical.py



*   system-backup.py

    This script automate system backups thanks to rdiff-backup and rsync. It is based on an idea from the "[Backup up on unreliable link](http://wiki.rdiff-backup.org/wiki/index.php/BackupUpOnUnreliableLink)" article from the [official rdiff-backup wiki](http://wiki.rdiff-backup.org).

*   website-backup.py

    This script automate the mirroring of several external websites (both files and MySQL databases) thanks to `lftp`, `mysqldump`, `ssh` and `rsync`. Then it make an incremental backup each day thanks to rdiff-backup and finally a snapshot each month. Here is the list of [latest changes and detailed features](http://kevin.deldycke.com/2007/03/website-backup-script-mysql-dumps-and-ssh-supported/).

*   xwd2png.py

    This script convert .xwd images taken with xvidcap to a series of .png images. I wrote this because mencoder can’t read xwd files.

*   zenphoto-to-wordpress.py


Licence
-------

Unless otherwise noted, code in this repository is distributed under a GNU GPL2+ licence.


Disclaimer
----------

All the code here is provided as is and with no guarentee - back up your data first, I am not responsible for anything bad that happens to you as a result of using my hacks.


Author
------

Kevin Deldycke. Find me at http://kevin.deldycke.com .
