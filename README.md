Description
-----------

This repository is a collection of tiny utility scripts, patches and hacks.

These are mostly one-time scripts, very old and very specific. I doubt you'll be able to use them as-is. Until you update and tweak them to fit your needs.

And if by chance you fix some bugs or add new features, feel free to submit a pull request. I'll be happy to merge it.

The code here is generally poorly written. Either because my coding style has improved since I wrote them, or because I didn't bother to make the code elegant after I finished my first working iteration.

If for any reason one of these script get momentum, I'll consider moving it to a stand-alone and dedicated project. This [already happened in the past with `maildir-deduplicate.py`](http://kevin.deldycke.com/2013/06/maildir-deduplicate-moved/).


Current content
---------------

*   **adsl-monitoring.py**

    Used with `cron`, it helps me to keep my unreliable broadband access alive.

    Context: http://kevin.deldycke.com/2004/06/mise-en-place-paserelle-adsl-mandrake-10/

*   **audio-file-normalizer.py**

    Parse a `.m3u` playlist file and convert Ogg/Vorbis and Flac files to AAC.

*   **avi2mp4.py**

    Converts Avi files within the folder to compressed MP4/MP3 movies. Codecs parameters are adapted for tiny films taken with my cheap camera. This is VLC-based but older version were based on mplayer/mencoder.

    Based on: http://kevin.deldycke.com/2006/11/video-commands/

*   **bbpress-to-mailbox.py**

    More details at: http://kevin.deldycke.com/2012/10/converting-bbpress-forum-mailbox-archive/

*   **bbpress-to-wordpress.py**

    More details at: http://kevin.deldycke.com/2012/10/transfer-bbpress-to-plain-wordpress/

*   **confsaver.py**

    Save a collection of files and directories into a Bzip2 compressed archive.

*   **cron-monitor-network.py**

*   **crop-tiff-images.py**

    Crops big tiff files in the folder one by one. I wrote this script as a stupid but working workaround to ImageMagick which wasn't able to handle too many files at once (at least on my Mandriva 2005, it always crash after several files processed).

*   **findDuplicates.py**

    This script search and display all duplicate files within a folder structure.

    Also see: http://kevin.deldycke.com/2006/10/find-duplicate-files-in-a-folder/

*   **getAgentList.py**

*   **KnewstickerToAkregator.py**

    Parse the KNewsTicker configuration file of the current logged user to extract feeds references. Then the script generate a OPML/XML file that can be imported to [Akregator](http://akregator.kde.org/). Prerequisite: KNewsTicker and pyxml.

    Also see: https://bugs.kde.org/show_bug.cgi?id=85477

*   **KopeteChatRenderer.py**

    Transform a Kopete history XML file to an ASCII file. I’ve written this script to be able to copy and paste my chat with pals in e-mails.

*   **la-bas.org-archive-download.py**

    Similar to `osdir-slideshow.py` but designed to download Ogg archives of a french radio show thanks to wget.

*   **linked_list.py**

    Implement a linked list class and its utility methods.

*   **maildir2ical.py**

    More details at: http://kevin.deldycke.com/2010/06/subversion-commits-mail-activity-stream-icalendar/

*   **maildir++2kmail.py**

    Import a [Maildir++](http://en.wikipedia.org/wiki/Maildir#Maildir.2B.2B) directory and its subfolders to [Kmail](http://kontact.kde.org/kmail).

    More details at: http://kevin.deldycke.com/2007/11/how-to-import-a-maildir-folder-to-kmail/

*   **mail_ingestor.py**

    More details at: http://kevin.deldycke.com/2012/09/mail-ingestor-py-ingest-raw-text-files-produce-mailbox/

*   **mass-replace.py**

*   **mechanize-playground.py**

*   **mldonkey-auto-download.sh**

    Combined with a cron entry, this script scan a given folder and auto start downloading torrent files found in that folder. Based on mldonkey and wget.

*   **monthly-internet-uptime.py**

    Monitor how long my backup Dial-up modem is up per month.

*   **osdir-slideshow.py**

    Get a series of screenshots from well-known OSdir slideshows.

*   **phorum_anon2user.php**

    Let you assign an owner to an anonymous post in Phorum.

*   **phorum_bodies_update.php**

    Convert old message format to new format (with the conversion of HTML tags to Phorum specific tags).

*   **phorum_to_e107.php**

    Migrate [Phorum 3.x](http://www.phorum.org) datas to a new empty e107 website. The destination e107 platform must be empty because this script copy Phorum id and don’t re-index database records.

*   **phorum-to-wordpress.py**

*   **process-monitoring.py**

    Combined with cron, helps keep an eye on a running process.

*   **qlc-effects-generator.py**

    More details at: http://kevin.deldycke.com/2010/08/qlc-effects-generator-led-panels/

*   **svn2ical.py**

    More details at: http://kevin.deldycke.com/2010/06/subversion-commits-mail-activity-stream-icalendar/

*   **system-backup.py**

    Automate system backups thanks to rdiff-backup and rsync. It is based on an idea from the "[Backup up on unreliable link](http://wiki.rdiff-backup.org/wiki/index.php/BackupUpOnUnreliableLink)" article from the [official rdiff-backup wiki](http://wiki.rdiff-backup.org).

*   **website-backup.py**

    Automate the mirroring of several external websites (both files and MySQL databases) thanks to `lftp`, `mysqldump`, `ssh` and `rsync`. Then it make an incremental backup each day thanks to rdiff-backup and finally a snapshot each month. Here is the list of [latest changes and detailed features](http://kevin.deldycke.com/2007/03/website-backup-script-mysql-dumps-and-ssh-supported/).

*   **xwd2png.py**

    Convert .xwd images taken with xvidcap to a series of .png images. I wrote this because mencoder can’t read xwd files.

*   **zenphoto-to-wordpress.py**

    More details at: http://kevin.deldycke.com/2012/09/zenphoto-wordpress-migration/


Past content
------------

*   **maildir-deduplicate.py**

    Moved to [its own repository](https://github.com/kdeldycke/maildir-deduplicate).

*   **ubuntu-install.sh** & **osx-install.sh**

    Moved to a [dedicated repository](https://github.com/kdeldycke/dotfiles).


License
-------

This software is licensed under the [GNU General Public License v2 or later
(GPLv2+)](LICENSE).


Disclaimer
----------

All the code here is provided as is and with no guarentee - back up your data first, I am not responsible for anything bad that happens to you as a result of using my hacks.


Author
------

Kevin Deldycke. Find me at http://kevin.deldycke.com .
