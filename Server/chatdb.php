<?php


//IMSafe Encrypted Chatroom Server Software
//http://www.FullOfEpicWin.com/imsafe/

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

ini_set("post_max_size", "20M");

class chatdb{
	//Put your own database info here!
	public $dbname = "dbname";
	public $dbuser = "dbuser";
	public $dbpassword = "dbpassword";
	public $dbhost = "localhost";

	function __construct(){
		$connection = mysql_connect($this->dbhost, $this->dbuser, $this->dbpassword);// or die('unable to connect!');
		mysql_select_db($this->dbname) or die("Unable to access database! " . mysql_error());
		$this->create_tables();  //Configure the database for use
		$this->deleteOldUsers(); //Delete any users who have timed out due to inactivity
	}
	
	function deleteOldUsers(){
		$expiration = time()-60; //Users are automatically signed off after 5 minutes of inactivity
		$sql ="DELETE FROM users WHERE lastAction <".$expiration;
		$result = mysql_query($sql);
	}
	
	function create_tables(){
		$sql="CREATE TABLE IF NOT EXISTS users(
			username VARCHAR(255) NOT NULL,
			room VARCHAR(255) NOT NULL,
			lastAction INT
			)";
			
		$result = mysql_query($sql);

		$sql="CREATE TABLE IF NOT EXISTS messages(
			room VARCHAR(255) NOT NULL,
			id INT(11) NOT NULL auto_increment,
			fromUser VARCHAR(255) NOT NULL,
			toUser VARCHAR(255) NOT NULL,
			message BLOB NOT NULL,
			unixTime INT,
			time TIMESTAMP,
			type VARCHAR(32),
			PRIMARY KEY (id)
			 )";
			
		$result = mysql_query($sql);
	}
	
	function addUser($username, $chatroom){
		//Add a use to the databas when they first log on
		//$sql = "SELECT COUNT(*) FROM customers WHERE user_id='test'"
		
		$sql="INSERT into users (username, lastAction, room) VALUES (\"$username\", ".time().", \"$chatroom\")";
		$result = mysql_query($sql);
		if(!$result){
			die('Error: ' . mysql_error());
		}
	}
	
	function disconnectUser($username, $chatroom){
		$sql = "DELETE FROM users WHERE username=\"$username\" AND room = \"$chatroom\"";
		$result = mysql_query($sql);
	}

	function getOnlineUsers($chatroom){
		//Return an array containing all the usernames currently using the chatroom
		$users = array();
		
		$sql = "SELECT * FROM users WHERE room = \"$chatroom\"";
		$result = mysql_query($sql);
		if(!$result){
			echo "<br/>MySql Error: ".mysql_error();
		}
		
		while($row = mysql_fetch_row($result)){
			array_push($users, $row[0]);
		}
		
		return $users;
	}
	
	function addMessage($fromUser, $message, $chatroom, $options){
		//$options is a dictionary style array that will specify private messaging in the future, currenlty only used to specify first person messages
		//The database structure currently supports private messaging, but is only being used like a chatroom for now
		$users = $this->getOnlineUsers($chatroom);
	
		foreach($users as $user){
			$sql = "INSERT INTO messages (room, fromUser, toUser, message, unixTime, type) VALUES (\"$chatroom\", \"$fromUser\", \"$user\", \"$message\", ".time().",\"". $options['type'] ."\")";
			mysql_query($sql);
		}
	}
	
	function getMessagesForUser($username, $recipts, $chatroom){
	 /* Returns a list of messages for "username", and deletes messages that have a confirmed recipt.
	    Messages are NOT DELETED unless a recipt is recieved, this is to avoid dropped messages. */
		
		//First, lets update the user's lastActivity value
		$sql = "UPDATE users SET lastAction = ".time()." WHERE username=\"$username\" AND room = \"$chatroom\"";
		$result = mysql_query($sql);
	   
	    $sql = "SELECT * FROM messages WHERE toUser=\"$username\" AND room = \"$chatroom\"";
		$result = mysql_query($sql);
		$onResult = 0;
		$usernameDisplay = ""; //How the username is displayed
		$allMessages = array();
		
		#<message_separator> seperates the different messages, while <time_separator> separates the timestamp and username from the message
		while($row = mysql_fetch_array($result, MYSQL_ASSOC)){
			if ($row["type"] == 'first_person'){ //To allow for /me to show as a "first persosn" message
				//Display a "first person" message
				$usernameDisplay = $row["fromUser"]." ";
			}
			else{
				//Display the messasge regularly, with a timestamp
				$usernameDisplay = "#".$row["fromUser"]." (".date("g:i.s a", strtotime($row["time"]))."): ";
			}
			
			//Add message to the array that will be sent back to the user
			array_push($allMessages, $usernameDisplay."<time_separator>".$row["id"]."<time_separator>".$row["message"]);

			$onResult++;
		}
		
		mysql_free_result($result);
		
		//Recipts are in the form  of a comma separated string of message IDs
		//This deletes all the messages with the ID corresponding to a recipt
		if($recipts != "None"){
			foreach(explode(",", $recipts) as $recipt){
				$sql = "DELETE FROM messages WHERE id = $recipt";
				$result = mysql_query($sql);
			}
		}
		//Send the requested messages to the user, separated by a distinct identifier. The identifiers long length will prevent
		//The encryption algorithm from accidently messing up the results
		return implode("<message_separator>", $allMessages);
	}
}


?>