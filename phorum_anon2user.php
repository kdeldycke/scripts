<?php
/*
+---------------------------------------------------------------+
|   Script to give ownership to anonymous posts.
|
|   Tested with : - phorum version 3.4.2
|                 - apache 2.0.47 (Mandrake Linux/6mdk)
|                 - PHP version 4.3.3
|                 - mySQL version 4.0.15
|
|   (c)Kevin Deldycke 2004
|   http://www.funky-storm.com
|   kevin@funky-storm.com
|
|   Released under the terms and conditions of the
|   GNU General Public License (http://gnu.org).
+---------------------------------------------------------------+
*/


// set parameters for connexion to MySQL server
$cfg_Host    = "localhost";
$cfg_User    = "root";
$cfg_Pass    = "";

// set database source (must be a phorum forum)
$phorum_Base    = "Current_FS";
$phorum_ForumId = "1";


// start of main code
echo "<html><body><pre>Start of script.<br>\n";

// get the name of the table which contain the forum we want to convert
$db_connect_id = mysql_connect($cfg_Hote, $cfg_User, $cfg_Pass);
$sql  = "SELECT `id`, `table_name`, `name` ";
$sql .= "FROM `forums` ";
$sql .= "WHERE `id` = 1";
$result  = mysql_db_query($phorum_Base, $sql);
$result2 = mysql_fetch_array($result);
$post_table = $result2['table_name'];
echo "Forum '".$result2['name']."' found.<br>\n";

// apply ownership change to database content ?
if (!empty($_POST['action'])) {
    $action = $_POST['action'];
    if ($action == 'set_owner') {
        // get the last message id
        $sql  = "SELECT `id` ";
        $sql .= "FROM `".$post_table."` ";
        $sql .= "ORDER BY `id` DESC";
        $results = mysql_db_query($phorum_Base, $sql);
        $msg_id = mysql_fetch_array($results);
        $last_id = $msg_id['id'];
        // get all posted data and create a table that contain all new ownership
        for ($id = 0; $id <= $last_id; $id++) {
            if (!empty($_POST['message'.$id])) {
                if ($_POST['message'.$id] != 0) {
                    $new_ownership["$id"] = $_POST['message'.$id];
                }
            }
        }
        // update new ownership into the database
        while (list($msg_id, $owner_id) = each($new_ownership)) {
            $sql  = "UPDATE `".$post_table."` ";
            $sql .= "SET `userid` = '".$owner_id."' ";
            $sql .= "WHERE `id` = '".$msg_id."' LIMIT 1";
            mysql_db_query($phorum_Base, $sql);
            echo "Message n#".$msg_id." new owner id: ".$owner_id."<br>";
        }
        // exit the script and print a successful message
        echo "End of ownership change.";
        echo "\n</pre></body></html>";
        exit();
    }
}

// get all message headers
$sql  = "SELECT * ";
$sql .= "FROM `".$post_table."` ";
$sql .= "WHERE `userid` = 0";
$results = mysql_db_query($phorum_Base, $sql);

// get all users
$sql  = "SELECT `id`, `username`, `email` ";
$sql .= "FROM `forums_auth` ";
$user_list = mysql_db_query($phorum_Base, $sql);

// create a constant string to display the dropdown list of users
$dropdown_list = "<option value=\"0\" selected=\"selected\">Anonymous</option>";
while ($user = mysql_fetch_array($user_list)) {
    $dropdown_list .= "<option value=\"".$user['id']."\">".$user['username']." [".$user['email']."]</option>";
}
$dropdown_list .= "</select>";

// print the header of the table
echo "<form action=\"phorum_anon2user.php\" method=\"post\">";
echo "Set the ownership for every anonymous post:<br>\n";
echo "<input type=\"hidden\" name=\"action\" value=\"set_owner\">";
echo "<table border=\"1\" cellpadding=\"4\" cellspacing=\"0\">";
echo "<tr valign=\"top\">";
echo "<td><b>id</b></td>";
echo "<td><b>Subject</b></td>";
echo "<td><b>Author [email]</b></td>";
echo "<td><b>Owner</b></td>";
echo "</tr>";

// scan every anonymous message
while ($msg = mysql_fetch_array($results)) {

    echo "<tr valign=\"top\">";
    echo "<td>".$msg['id']."</td>";
    echo "<td>".$msg['subject']."</td>";
    echo "<td>".$msg['author']." [".$msg['email']."]</td>";
    echo "<td>";

    // create a dropdown list of all authenticated users
    echo "<select name=\"message".$msg['id']."\">";
    echo $dropdown_list;

    echo "<input type=\"submit\" name=\"set\" value=\"set\">";

    echo "</td>";
    echo "</tr>";
}

echo "</table></form>";
echo "\n</pre></body></html>";

?>
