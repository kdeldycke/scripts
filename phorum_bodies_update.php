<?php
/*
+---------------------------------------------------------------+
|
| Script to convert old message format to new format (with
| the conversion of html tags to phorum specific tags)
|
|-- Tested with
|
| phorum version 3.4.2
| apache 2.0.47 (Mandrake Linux/6mdk)
| PHP version 4.3.3
| mySQL version 4.0.15
|
|-- Precautions
|
| Run this script only on a selection of old message.
| Don't apply this script on new phorum message !
|
|-- Copyright
|
| (c)Kevin Deldycke 2004
| espadrilles at free dot fr
|
| Released under the terms and conditions of the
| GNU General Public License (http://gnu.org).
|
|-- History
|
| v0.1 2004-04-17
| First public release at http://phorum.org/mods/read.php?f=4&i=1215&t=1215
|
+---------------------------------------------------------------+
*/


// set parameters for connexion to MySQL server
$cfg_Host    = "localhost";
$cfg_User    = "root";
$cfg_Pass    = "";

// set database source (must be a phorum forum)
$phorum_Base    = "phorum";
$phorum_ForumId = "1";

// set the message "threshold"
// $id_limit is the id of the first phorum message posted in the new version
// when the convertion proccess reach this message, the script stop
$id_limit = 0;


// start of main code
echo "<html><body><pre>Start of convertion script.<br>\n";

// get the name of the table which contain the forum we want to convert
$db_connect_id = mysql_connect($cfg_Hote, $cfg_User, $cfg_Pass);
$sql  = "SELECT `id`, `table_name`, `name` ";
$sql .= "FROM `forums` ";
$sql .= "WHERE `id` = 1";
$result  = mysql_db_query($phorum_Base, $sql);
$result2 = mysql_fetch_array($result);
$msg_table = $result2['table_name'];
$msg_bodies = $msg_table."_bodies";
echo "Forum '".$result2['name']."' found.<br>\n";

// get all message bodies of the table
$sql  = "SELECT * ";
$sql .= "FROM `".$msg_bodies."` ";
$sql .= "WHERE `id` < ".$id_limit;
$results = mysql_db_query($phorum_Base, $sql);
echo "Get all messages bodies...<br>";

// scan every message until the limit
while($msg = mysql_fetch_array($results)) {

    // replacement rules
    $search = array("'<i>'i", "'</i>'i",
                    "'<b>'i", "'</b>'i",
                    "'<u>'i", "'</u>'i",
                    "'</a>'i",
                    "'<a (.*)href=\"([^\"]*)\"(.*)>'i"
                    );
    $replace = array(   "[i]", "[/i]",
                        "[b]", "[/b]",
                        "[u]", "[/u]",
                        "[/url]",
                        "[url=\\2]"
                        );
    $new_body = preg_replace($search, $replace, $msg['body']);

    // save the transformations to the database
    $new_body = addslashes($new_body);
    $sql  = "UPDATE `".$msg_bodies."` SET ";
    $sql .= "`body`='".$new_body."' ";
    $sql .= "WHERE `id`='".$msg['id']."' LIMIT 1";
    mysql_db_query($phorum_Base, $sql);

    echo "Message n#".$msg['id']." updated.<br>";
}

echo "\nEnd of script.<br></pre></body></html>";

?>
