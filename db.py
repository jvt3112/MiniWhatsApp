# importing pymongo library to use with MongoDB database
from pymongo import MongoClient

# class DB that have performs all the database 
# operations, includes checking for accounts exsistence
# register an account, update status in DB, get password
# from the DB, get status form the DB, to check for whether  
# account is online or not, user login, logout and ip,port
# details

class DB:

    # db initializations
    # using local mogodb compass to monitor the databases
    def __init__(self):
        # initializing monogClient
        self.client = MongoClient('mongodb://localhost:27017/')
        # setting name for db as miniWhatsApp
        self.db = self.client['miniWhatsApp'] 

    # registers a user and sets by default status for every new user
    def register(self, username, password, status):
        # account details include username, password, status
        account = {
            "username": username,
            "password": password,
            "status": status 
        }
        # insersts account in db
        self.db.peerAccount.insert(account)

    # checks if an account with the username exists
    def is_account_exist(self, username):
        # finds username in database
        # return true if exists and false otherwise
        if self.db.peerAccount.find({'username': username}).count() > 0:
            return True
        else:
            return False

    # updates the status with given username and new status
    def update_status(self,username,status):
        # finds the username
        itm = self.db.peerAccount.find_one({'username': username})
        # updates the status with usernames object id
        self.db.peerAccount.update({"_id":itm.get('_id')}, {'$set': {"status":status}})

    # extracts the password for a given username
    def get_password(self, username):
        # returns the password for a given username
        return self.db.peerAccount.find_one({"username": username})["password"]
    
    # gets status for a given username
    def get_status(self, username):
        # returns status of the user
        return self.db.peerAccount.find_one({"username": username})["status"]

    # extracts the ip address and the port number of the username
    def get_peer_ip_port(self, username):
        # finds the user and returns its ip and port
        res = self.db.onlinePeer.find_one({"username": username})
        return (res["ip"], res["port"])

    # checks if an account with the username is online or not
    def is_account_online(self, username):
        # returns true if the peer is online and false otherwise
        if self.db.onlinePeer.find({"username": username}).count() > 0:
            return True
        else:
            return False

    # when user logs in databases stores its online nature by creating another
    # filed called online peers and stores its ip, port and username
    def user_login(self, username, ip, port):
        online_peer = {
            "username": username,
            "ip": ip,
            "port": port
        }
        # insersts account in db
        self.db.onlinePeer.insert(online_peer)
    

    # logs out the user from the online peers list in db
    def user_logout(self, username):
        self.db.onlinePeer.remove({"username": username})