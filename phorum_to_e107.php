<?php
/*
+---------------------------------------------------------------+
|   Script to migrate phorum threads to e107 forum.
|
|   Tested with : - phorum version 3.4.2
|                 - e107 version v0.603 build Revision #6
|                 - apache 2.0.47 (Mandrake Linux/6mdk)
|                 - PHP version 4.3.3
|                 - mySQL version 4.0.15
|
|   This script is designed to migrate phorum datas to a new _empty_ e107 website. The destination e107 platform must be empty because this script copy phorum id and don't re-index database records. --> not true the moment, i try to keep this feature on
|
|   Date: 21 dec 2004
|
|   (c)Kevin Deldycke 2004
|   http://www.funky-storm.com
|   kevin@funky-storm.com
|
|   Released under the terms and conditions of the
|   GNU General Public License (http://gnu.org).
+---------------------------------------------------------------+
*/

/* TODO:
- manage groups
- manage users
- manage attachements
- manage permissions and rights on parents folder and forum using users and groups
- create a beautiful form using integrated css (to keep this script into a single file)
- copy commented header information in clear at top of the html form
- 'forum_datestamp', 'forum_moderators', 'forum_class' must be filled

*/


// function to convert a mysql datetimestamp to unix date format
function unix_date($date_in)
{
  sscanf($date_in, "%4s-%2s-%2s %2s:%2s:%2s", &$Y, &$M, &$D, &$h, &$m, &$s);
  return mktime($h, $m, $s, $M, $D, $Y);
}


// function to delete last chars of a string, only used in this script for the easy creation of SQL queries
function del_char(&$string, $n)
{
  $string = substr($string, 0, strlen($string)-$n);
}


// function to insert a row with given $properties in $table of '$db' database
function insertRow($properties, $table, $db)
{
  // create the INSERT sql query
  $sql = "INSERT INTO `".$table."` (";
  reset($properties);
  while($value = each($properties)) {
    $sql .= "`".$value[0]."`, ";
  }
  del_char($sql, 2);
  $sql .= ") VALUES (";
  reset($properties);
  while($value = each($properties)) {
    $sql .= "'".$value[1]."', ";
  }
  del_char($sql, 2);
  $sql .= ")";
  #echo "<br>SQL Query: ".$sql."<br><br>";  
  // send the query
  mysql_db_query($db, $sql);
  // return the id of the inserted row
  return mysql_insert_id();
}


// function to test if the string look like an ip address
function isIp($ip)
{
  $valid = true;
  $ip = explode(".", $ip);
  foreach($ip as $block) {
    if(!is_numeric($block)) {
      $valid = false;
    }
  }
  return $valid;
}    


// only usefull for debuging
function show_array($array)
{
  $output = "";
  for(reset($array); $key = key($array), $pos = pos($array); next($array)) {
    if(is_array($pos)) {
      $output .= "$key : <ul>";
      $output .= show_array($pos);
      $output .= "</ul>";
    } else { 
      $output .= "$key = $pos <br>";
    }
  }
  return $output;
}


// function to migrate all threads and message of a given forum
function migrateThreads($phorumTable, $forum_id)
{   
  global $phorum_db, $e107_threadTable, $e107_db, $memberIdTable;

  // select top thread messages (= parentless messages = start of a thread)
  $sql2  = "SELECT * ";
  $sql2 .= "FROM `".$phorumTable."`";
  $sql2 .= "WHERE `parent` = 0";
  $thread_list  = mysql_db_query($phorum_db, $sql2);

  // convert each message from Phorum to e107
  while($thread = mysql_fetch_array($thread_list)) {

    // get the body of the message (stored in a different table in phorum)
    $sql3  = "SELECT * ";
    $sql3 .= "FROM `".$phorumTable."_bodies` ";
    $sql3 .= "WHERE `id` = ".$thread['id'];
    $bodies = mysql_db_query($phorum_db, $sql3);
    $msg_body = mysql_fetch_array($bodies);

    // set the thread ownership
    // TODO: create a function for messages migration ?      
    // TODO: recursive call ?
    //if($thread['parent'] = 0) {
    //  $msg_parent = 0;
    //} else {
    //  $msg_parent = $thread['thread'];
    //}

    // set the thread moderation status
    if($thread['approved'] != 'Y') {
      $msg_active = 0;
    } else {
      $msg_active = 1;
    }

    // set the ownership string
    
    if($thread['userid'] == 0) {
      // get the ip of the anonymous poster not the host name
      if(isIp($thread['host'])) {
        $ip = $thread['host'];
      } else {
        // try to convert the hostname to ip
        $ip = gethostbyname($thread['host']);
        if(!isIp($ip)) {
          unset($ip);
        }
      }
      if(isset($ip)) {
        $ip = chr(1).$ip;
      }
      $msg_owner = "0.".addslashes($thread['author']).$ip;
    } else {
      $msg_owner = $memberIdTable[$thread['userid']];
    }
    
    // array to describe how to migrate every data of the thread
    $msg_tab = array( 'thread_name'       => addslashes($thread['subject'])
                    , 'thread_thread'     => str_replace("[%sig%]", "", addslashes($msg_body['body']))
                    , 'thread_forum_id'   => $forum_id
                    , 'thread_parent'     => 0
                    , 'thread_datestamp'  => unix_date($thread['datestamp'])
                    , 'thread_active'     => $msg_active
                    , 'thread_user'       => $msg_owner
                    );
    // add the message in the e107 forum
    $e107Thread_id = insertRow($msg_tab, $e107_threadTable, $e107_db);        
    $log .= "          New thread \"".stripslashes($thread['subject'])."\" added with its first message n°".$thread['id']."<br>";
  
    // TODO: this part of function is the same as above, so we can factorise this part  
    // get all messages sons of the current thread
    $log .= "            Get all messages of the thread...<br>";
    $sql3  = "SELECT * ";
    $sql3 .= "FROM `".$phorumTable."`";
    $sql3 .= "WHERE `thread` = ".$thread['id']." AND `parent` <> 0";
    $son_list  = mysql_db_query($phorum_db, $sql3);
    
    // convert each message from Phorum to e107
    while($son = mysql_fetch_array($son_list)) {
      // get the body of the message (stored in a different table in phorum)
      $sql4  = "SELECT * ";
      $sql4 .= "FROM `".$phorumTable."_bodies` ";
      $sql4 .= "WHERE `id` = ".$son['id'];
      $bodies = mysql_db_query($phorum_db, $sql4);
      $son_body = mysql_fetch_array($bodies);
      
      // set the thread moderation status
      if($son['approved'] != 'Y') {
        $son_active = 0;
      } else {
        $son_active = 1;
      }
      
      // set the ownership string
      if($son['userid'] == 0) {
        // get the ip of the anonymous poster not the host name
        if(isIp($son['host'])) {
          $ip = $son['host'];
        } else {
          // try to convert the hostname to ip
          $ip = gethostbyname($son['host']);
          if(!isIp($ip)) {
            unset($ip);
          }
        }
        if(isset($ip)) {
          $ip = chr(1).$ip;
        }
        $msg_owner = "0.".addslashes($son['author']).$ip;
      } else {
        $msg_owner = $memberIdTable[$son['userid']];
      }

      // array to describe how to migrate every data
      $son_tab = array( 'thread_name'       => addslashes($son['subject'])
                      , 'thread_thread'     => str_replace("[%sig%]", "", addslashes($son_body['body']))
                      , 'thread_forum_id'   => $forum_id
                      , 'thread_parent'     => $e107Thread_id
                      , 'thread_datestamp'  => unix_date($son['datestamp'])
                      , 'thread_active'     => $son_active
                      , 'thread_user'       => $msg_owner
                      );
      // add the message in the thread
      insertRow($son_tab, $e107_threadTable, $e107_db);        
      $log .= "            New son message \"".stripslashes($son_tab['thread_name'])."\" added to the thread.<br>";
    }
  }
  
  return $log;
}   

    
// capture all variables given by the post method
if(!empty($_POST['cfg_host'])) {
  $cfg_host = $_POST['cfg_host'];
}
if(!empty($_POST['cfg_user'])) {
  $cfg_user = $_POST['cfg_user'];
}
if(!empty($_POST['cfg_pass'])) {
  $cfg_pass = $_POST['cfg_pass'];
}
if(!empty($_POST['phorum_db'])) {
  $phorum_db = $_POST['phorum_db'];
}
if(!empty($_POST['phorum_mainTable'])) {
  $phorum_mainTable = $_POST['phorum_mainTable'];
}
if(!empty($_POST['e107_db'])) {
  $e107_db = $_POST['e107_db'];
}
if(!empty($_POST['e107_tablePrefix'])) {
  $e107_tablePrefix = $_POST['e107_tablePrefix'];
}
if(!empty($_POST['e107_defaultForumParentName'])) {
  $e107_defaultForumParentName = $_POST['e107_defaultForumParentName'];
}


// is there enough informations to start the migration ?
if(!empty($cfg_host) and !empty($cfg_user) and !empty($phorum_db) and !empty($phorum_mainTable) and !empty($e107_db) and !empty($e107_defaultForumParentName)) {

  $log .= "<pre>Start of migration script.<br>";

  // define e107 table names
  $e107_forumTable   = $e107_tablePrefix."forum";
  $e107_threadTable  = $e107_tablePrefix."forum_t";
  $e107_userTable    = $e107_tablePrefix."user";
  
  // define Phorum table names
  $phorum_membersTable = $phorum_mainTable."_auth";

  // try to connect to the mysql server
  $db_connect_id = mysql_connect($cfg_hote, $cfg_user, $cfg_pass) or die("MySQL error n°".mysql_errno()." when trying a connexion to the server: ".mysql_error());
  
  // get all members
  $log .= "<br><br><br>  Import all members...<br>";
  $sql  = "SELECT * ";
  $sql .= "FROM `".$phorum_membersTable."` ";
  $member_list = mysql_db_query($phorum_db, $sql);  
  
  // initialize a member id migration table
  // old id => new id
  $memberIdTable = array();
  
  // add every member in e107
  while($member = mysql_fetch_array($member_list)) {
    # TODO : be carefull user_name must be Unique
    # for jabber etc --> extended user field
    $memberProperties = array ( 'user_password'   => $member['password']
                              , 'user_name'       => addslashes($member['username'])
                              , 'user_login'      => addslashes($member['name'])
                              , 'user_email'      => $member['email']
                              , 'user_homepage'   => $member['webpage']
                              , 'user_icq'        => $member['icq']
                              , 'user_aim'        => $member['aol']
                              , 'user_msn'        => $member['msn']
                              , 'user_signature'  => addslashes($member['signature'])
                              , 'user_image'      => $member['image']
                              , 'user_hideemail'  => $member['hide_email']
                              );  
    $memberNewId = insertRow($memberProperties, $e107_userTable, $e107_db);        
    // keep a trace of the conversion
    $memberIdTable[$member['id']] = $memberNewId.".".addslashes($member['username']);
    $log .= "<br>    Member \"".$member['username']."\" has been added to e107.<br>";
  }
  
  // get all phorum folder
  $log .= "<br><br><br>  Import all folders...<br>";
  $sql  = "SELECT * ";
  $sql .= "FROM `".$phorum_mainTable."` ";
  $sql .= "WHERE `folder` = 1";
  $folder_list = mysql_db_query($phorum_db, $sql);
  
  // add all folders
  while($folder = mysql_fetch_array($folder_list)) {  
  
    // TODO: get folder accessibility rules and fit this in forum_class
    $folderProperties = array ( 'forum_name'      => addslashes($folder['name'])
                              , 'forum_class'     => 0
                              , 'forum_datestamp' => 0
                              );  
    $folderNewId = insertRow($folderProperties, $e107_forumTable, $e107_db);        
    $log .= "<br>    Phorum folder \"".$folder['name']."\" has been converted to e107 forum parent.<br>";
    
    // get all phorum forums of the current folder
    $log .= "      Import all forums of the folder \"".$folder['name']."\" ...<br>";
    $sql2  = "SELECT * ";
    $sql2 .= "FROM `".$phorum_mainTable."` ";
    $sql2 .= "WHERE `folder` = 0 AND `parent` = ".$folder['id'];
    $forum_list = mysql_db_query($phorum_db, $sql2);
    
    // migrate all forums of the current folder
    while($forum = mysql_fetch_array($forum_list)) {
      $forumProperties = array( 'forum_name'         => addslashes($forum['name'])
                              , 'forum_description'  => addslashes($forum['description'])
                              , 'forum_parent'       => $folderNewId
                              , 'forum_datestamp'    => 0
                              , 'forum_moderators'   => ""
                              , 'forum_class'        => ""
                              );
      $e107Forum_id = insertRow($forumProperties, $e107_forumTable, $e107_db);        
      $log .= "<br>        Forum \"".$forum['name']."\" added.<br>";
      
      // migrate all threads of this forum
      $log .= "          Get all threads of \"".stripslashes($forumProperties['name'])."\" forum...<br>";
      $log .= migrateThreads($forumProperties['table_name'], $e107Forum_id);
    }
  }
    
  // get all parentless phorum forums
  $log .= "<br><br><br>  Import all parentless forums...<br>";
  $sql  = "SELECT * ";
  $sql .= "FROM `".$phorum_mainTable."` ";
  $sql .= "WHERE `folder` = 0 AND `parent` = 0";
  $forum_list = mysql_db_query($phorum_db, $sql);
  
  // migrate all parentless forums
  while($forum = mysql_fetch_array($forum_list)) {
    // we need to create a default parent forum      
    // check if the default parent is not already created
    if(empty($e107_defaultParentId)) {
      // TODO: allow the user to choose the default class
      $defaultParentProperties = array( 'forum_name'       => addslashes($e107_defaultForumParentName)
                                      , 'forum_class'      => 0
                                      , 'forum_datestamp'  => 0
                                      );  
      $e107_defaultParentId = insertRow($defaultParentProperties, $e107_forumTable, $e107_db);        
      $log .= "<br>    Default parent forum \"".$e107_defaultForumParentName."\" for parentless Phorum forums added.<br>";
    }
    // create the forum
    $forumProperties = array( 'forum_name'         => addslashes($forum['name'])
                            , 'forum_description'  => addslashes($forum['description'])
                            , 'forum_parent'       => $e107_defaultParentId
                            , 'forum_datestamp'    => 0
                            , 'forum_datestamp'    => 0
                            , 'forum_moderators'   => ""
                            , 'forum_class'        => ""
                            );
    $e107Forum_id = insertRow($forumProperties, $e107_forumTable, $e107_db);        
    $log .= "<br>        Parentless forum \"".$forum['name']."\" added.<br>";
    
    // migrate all threads of this forum
    $log .= "          Get all threads of \"".stripslashes($forum['name'])."\" forum...<br>";
    $log .= migrateThreads($forum['table_name'], $e107Forum_id);
  }   

  $log .= show_array($memberIdTable);
    
  mysql_close($db_connect_id);
  $log .= "<br>End of script.</pre></body></html>";
  
}

// display the setup form
?>


<html>
<body>

<?php if(!empty($log)) {exit($log);} ?>

<h1>Phorum to e107 migration script - Setup</h1>

<form action="<?php echo $PHP_SELF; ?>" method="post">
* required<br>
<table border="1" cellpadding="4" cellspacing="0">
  <tr colspan="3">
    <td><b>MySQL parameters</b></td>
  </tr>
  <tr>
    <td>Host*</td>
    <td><input class="field" type="text" name="cfg_host" value="<?php if(!empty($cfg_host)){echo $cfg_host;}else{echo "localhost";}?>" size="20"></td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td>User login*</td>
    <td><input class="field" type="text" name="cfg_user" value="<?php if(!empty($cfg_user)){echo $cfg_user;}else{echo "root";}?>" size="20"></td>
    <td>&nbsp;</td>    
  </tr>
  <tr>
    <td>User password</td>
    <td><input class="field" type="text" name="cfg_pass" value="<?php if(!empty($cfg_pass)){echo $cfg_pass;}?>" size="20"></td>
    <td>Can be empty.</td>
  </tr>
  <tr colspan="3">
    <td><b>Phorum parameters</b></td>
  </tr>
  <tr>
    <td>Phorum database*</td>
    <td><input class="field" type="text" name="phorum_db" value="<?php if(!empty($phorum_db)){echo $phorum_db;}else{echo "phorum_db";}?>" size="20"></td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td>Main table name*</td>
    <td><input class="field" type="text" name="phorum_mainTable" value="<?php if(!empty($phorum_mainTable)){echo $phorum_mainTable;}else{echo "forums";}?>" size="20"></td>
    <td>&nbsp;</td>
  </tr>
  <tr colspan="3">
    <td><b>e107 parameters</b></td>
  </tr>
  <tr>
    <td>e107 database*</td>
    <td><input class="field" type="text" name="e107_db" value="<?php if(!empty($e107_db)){echo $e107_db;}else{echo "e107";}?>" size="20"></td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td>Table prefix</td>
    <td><input class="field" type="text" name="e107_tablePrefix" value="<?php if(!empty($e107_tablePrefix)){echo $e107_tablePrefix;}else{echo "e107_";}?>" size="20"></td>
    <td>&nbsp;</td>
  </tr>
  <tr>
    <td>Default forum parent name*</td>
    <td><input class="field" type="text" name="e107_defaultForumParentName" value="<?php if(!empty($e107_defaultForumParentName)){echo $e107_defaultForumParentName;}else{echo "Main forums";}?>" size="20"></td>
    <td>This name is only use to create a default parent in the case where phorum forums without parent are found. It's needed because e107 don't allow forum without parent.<br>By default, the e107 parent of all parentless Phorum forums is visible by everyone (class=public).<br>Because e107 disallow sub-folder, this script will create a parent forum at top level for each folder (and sub folder) found.</td>
  </tr>
  <tr colspan="3">
    <td><input class="field" type="submit" name="submit" value="Start the migration"></td>
  </tr>
</table>
</form>

</body>
</html>