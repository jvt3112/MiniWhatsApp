from pymongo import MongoClient

# Includes database operations
class DB:


    # db initializations
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['p2p-chat'] #p2p-chat


    # checks if an account with the username exists
    def is_account_exist(self, username):
        if self.db.accounts.find({'username': username}).count() > 0:
            return True
        else:
            return False

    # registers a user
    def register(self, username, password, status):
        account = {
            "username": username,
            "password": password,
            "status": status 
        }
        print(status)
        self.db.accounts.insert(account)

    def update_status(self,username,status):
        #db.city.update({_id:ObjectId("584a13d5b65761be678d4dd4")}, {$set: {"citiName":"Jakarta Pusat"}})
        itm = self.db.accounts.find_one({'username': username})
        self.db.accounts.update({"_id":itm.get('_id')}, {'$set': {"status":status}})
        #if self.db.accounts.find({'username': username}).count() > 0:

    # retrieves the password for a given username
    def get_password(self, username):
        return self.db.accounts.find_one({"username": username})["password"]
    
    def get_status(self, username):
        return self.db.accounts.find_one({"username": username})["status"]

    # checks if an account with the username online
    def is_account_online(self, username):
        if self.db.online_peers.find({"username": username}).count() > 0:
            return True
        else:
            return False

    # logs in the user
    def user_login(self, username, ip, port):
        online_peer = {
            "username": username,
            "ip": ip,
            "port": port
        }
        self.db.online_peers.insert(online_peer)
    

    # logs out the user 
    def user_logout(self, username):
        self.db.online_peers.remove({"username": username})
    

    # retrieves the ip address and the port number of the username
    def get_peer_ip_port(self, username):
        res = self.db.online_peers.find_one({"username": username})
        return (res["ip"], res["port"])