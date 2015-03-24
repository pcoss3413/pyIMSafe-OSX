<?php
//IMSafe Encrypted Chatroom Server Software
/*
*  Copyright (C) 2014  Patrick T. Cossette
*
*  This program is free software; you can redistribute it and/or
*  modify it under the terms of the GNU General Public License
*  as published by the Free Software Foundation; either version 2
*  of the License, or (at your option) any later version.
*  
*  This program is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*  GNU General Public License for more details.
*  
*  You should have received a copy of the GNU General Public License
*  along with this program; if not, write to the Free Software
*  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
*/

//Created By: Patrick T. Cossette
//http://www.DigitalDiscrepancy.com

include 'chatdb.php';
$chat = new chatdb();

//Configure your whitelist and  blacklist  parameters here
//1 = use list
//0 = ignore list
$useWhitelist = 0;
$useBlacklist = 0;
$whitelist= array(); // Enter whitelist usernames here
$blacklist= array(); // Enter blacklist usernames here

if(!isset($_POST["username"]) || !isset($_POST["message"])){
		//This page was most likely accessed through a browser..
		?>
  		<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
        <html>
            <head>
            <title>IMSafe Server</title>
                <BODY><center><h2><br/><br/>
                Welcome to the IMSafe Server page!<br/> If you are looking to download IMSafe, you can find the latest versions <a href="http://www.fullofepicwin.com/imsafe">here</a>.<br/>
                <br/<br/></h2><h3>
                Otherwise, please refer to IMSafe's home page for help on how to use this software!</h3>
                </center>
                <br/>
                
                </BODY>
        </HTML>
     	<?php   
	}
    else{
		if(isset($_GET["room"])){
			$chatroom = $_GET["room"];
		}
		else{
			$chatroom = "Main";
		}
		
		if($_POST["message"] == "connect_request"){ 
			//A new user is attempting to connect, make sure  the username doesn't conflict with the whitelist/blacklist
			if((!$useWhitelist || in_array($_POST["username"], $whitelist)) && (!$useBlacklist || !in_array($_POST["username"], $blacklist))){
				if(!in_array($_POST["username"], $chat->getOnlineUsers($chatroom))){
					//Check  to see if the username is already in the users table, if not, add it.
					$chat->addUser($_POST["username"], $chatroom);
				}
				echo "Connection Successful";
			}
			else{
				echo "Connection Failed, ".$_POST["username"];
			}
			
		}
		else if (isset($_POST["prg"])){
			//prg represents what function the user is requesting to execute
			if ($_POST["prg"] == "list"){
				echo implode(",", $chat->getOnlineUsers($chatroom)); //Return a list of users as comma separated values
			}
			else if ($_POST["prg"] == "update"){
				//retrieve any new messages and delete messages that have  already been recieved
				$chatroomUpdate = $chat->getMessagesForUser($_POST["username"], $_POST["recipts"], $chatroom);
				echo $chatroomUpdate;
			}
			else{ 
				// Disconnect user
				$chat->disconnectUser($_POST["username"]);
			}
		}
		else{
			//The user is sending message to the chatroom
			//Currenlty 'options' only supports first person messages, but will also make private messaging  possible in the future
			$options = array();
			$options['type'] = 'normal';
			
			if(isset($_POST["options"])){
				//In the future, process the "options" string into a dictionary style array before sending it to the addMessage function
				$options['type'] = 'first_person';
			}
			
			//Send the message to the database
			$chat->addMessage($_POST["username"], $_POST["message"], $chatroom, $options);
		}
}

?>