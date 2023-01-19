import pymongo

class mongo():
    def __init__(self):
        #establish connections with the local server of mongo
        hostMongo  = 'mongodb://localhost:27017/'
        connection = pymongo.MongoClient(hostMongo, connect=False,\
                    maxPoolSize=None, serverSelectionTimeoutMS=500)
        self.db = connection.shake_api
        self.is_connected = True

        #test to know if the connection was established or not
        try:
            connection.admin.command('ismaster')
        except:
            #if not save the state to use files instead of db
            self.is_connected = False

    #insert a document in the specified collection
    def insert(self, collection, data):
        query =  self.db[collection].insert_one(data)
        if query:
            return True
        else:
            return False
    
    #get all the documents stored in a specified collection
    def find(self, collection):
        query = self.db[collection].find({},{"_id" : 0})
        return query

    #get all the documents stored in a specified 
    #collection that match the provided condition
    def search(self, collection, condition):
        query = self.db[collection].find(condition,{"_id" : 0})
        return query

