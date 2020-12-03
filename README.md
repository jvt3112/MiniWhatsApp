# MiniWhatsApp
                        
# Initialization:
To download the Mini-Whatsapp github repository, we need to clone it using the following command:</br>
git clone the repository</br>
You need to do setup to fulfill requirements:</br>
Its installation process can be seen here : [Link](https://docs.mongodb.com/manual/tutorial/install-mongodb-enterprise-on-windows/)</br>
Once installed, run MongoDB compass and connect the database, so that you can analyse the database as the application is run.</br>
## Some of the python libraries required are :</br>
* threading </br>
* pymongo</br>
* stdiomask </br>
* select</br>
# After downloading and setting up:</br>
To set up our Mini-Whatsapp, we first need to start up the main server (registry.py). </br>
Simply run the following command:</br>
` python registry.py ` </br>
Now the user can start using Mini-Whatsapp by starting the chat program (peer.py) using the following command.<br/>
` python peer.py ` </br>
</br>
Note: The peer connects to the registry using its IP address which will be displayed on the registry side. Also it can be hard-coded if convenient.
# Main features:
There are many features that have been packed into this application. Namely:
1. Create Account: Create an account to use Mini-Whatsapp. You will have to provide a unique username and a password.
2. Login: Log into Mini-Whatsapp using the account created previously. You will have to provide a username and password to login. You also need to specify the port that you should use to start the peer client (More details in the ‘Communication and Connection Maintenance’ section). Password is masked for the purpose of security.
3. Logout: Logout from your current session of Mini-Whatsapp. You will then exit the application.
4. Search: Search for a particular user using their username.
5. Start Chat: Using the username of a user you can send a request to the user to start a chat session with them. On the receiver-side the user will receive a chat request pop-up where they must type “OK” to start the chat. There is also another option of “OK-SAVE” which the user can choose to save the chat messages. Using ":q" we can quit the chat. ":f" flag during the chat is used for file sharing. 
6. Change Status: The user can change their status using this command. The user will have a default status (a description in text). He/She can choose to change the status if he/she wishes to do so.
7. See Status: The user can view the status of any user by entering the username of the user. 
8. Start Group Chat: The user can also create a group chat with any number of users. The port for the group chat server must also be specified. The user will be able to add the users by entering their names and sending requests to each user. "OK-GROUP-portno." is the message to be sent by acceptor. Group chat can be exited using "QUIT"command. </br>

For more details : see the report.
