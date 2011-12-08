FOLDER              = "/var/www"
excluded_folders    = [".svn",]
excluded_extensions = [ "mpg", "avi", "mov", "mkv", "divx", "vob", "mp4"
                      , "swf", "flv"
                      , "png", "gif", "jpg", "jpeg", "ico", "xcf"
                      , "pdf", "doc"
                      , "mp3", "flac", "ogg", "wav", "aac"
                      , "vdi", "vmdk", "qcow", "iso"
                      , "sqlite"
                      , "bz2", "zip", "gz", "rpm", "rar", "7z"
                      ]
replace_list   = [ ("/var/www/www.coolcavemen.com"         , "/var/www/coolcavemen")
                 , ("/var/www/kev.coolcavemen.com"         , "/var/www/deldycke.kevin")
                 , ("/var/www/www.funky-storm.com"         , "/var/www/funky-storm")
                 , ("/var/www/justinespace.coolcavemen.com", "/var/www/justinespace")
                 , ("/var/www/www.maomium.com"             , "/var/www/maomium")
                 , ("/var/www/qpx.lich-ti.fr"              , "/var/www/qpx")
                 , ("/var/www/qpx.coolcavemen.com"         , "/var/www/qpx")
                 , ("http://www.coolcavemen.com"           , "http://coolcavemen.com")
                 , ("http://kev.coolcavemen.com"           , "http://kevin.deldycke.com")
                 , ("http://www.funky-storm.com"           , "http://funky-storm.com")
                 , ("http://www.maomium.com"               , "http://maomium.com")
                 , ("http://qpx.lich-ti.fr"                , "http://qpx.coolcavemen.com")
                 ]

getSafeString = lambda s: s.replace('/', '\/').replace('.', '\.')

file_filter = ' '.join(['-not -iname "*\.%s"' % getSafeString(ext.lower()) for ext in excluded_extensions])

# the double -regex ".*%s$" and ".*%s\/.*" parameter below should have been something like ".*%s(\/.*|$)" but find command doesn't seems to support alternative syntax in regexps
folder_filter = ' '.join(['-not -regex ".*\/%s\/.*"' % getSafeString(folder) for folder in excluded_folders])

for (source, dest) in replace_list:
  cmd = """find %s -mount -type f %s %s -print -exec sed -i 's/%s/%s/g' "{}" \;""" % (FOLDER, folder_filter, file_filter, getSafeString(source), getSafeString(dest))
  print cmd
  # Create a file to attest the end of the job
  print """echo "`date`" > ./%s""" % source.replace('/', '-').replace(':', '-').replace('.', '-')


# clean up bad sed temporary files
# find /var/www -iname "sed*"

# How to use:
# python ./mass-replace.py > migration.sh
# chmod 755 ./migration.sh
# nohup ./migration.sh &
