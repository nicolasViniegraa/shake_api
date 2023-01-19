from cryptography.fernet import Fernet
from base64 import b64encode
from os import path

'''
    IMPORTANT

    The encrypt() and decrypt() methods used to secure the credentials
    receive and return a variable in bytes format, so before or after 
    calling encrypt() and decrypt() the variables are encoded or 
    decoded in utf-8

'''

#create the key for encryption and store it if the key.txt file doesn't exist
def set_key():

    #check if the file key.txt isn't already created
    if not path.exists("key.txt"):

        #if not create the key
        key = Fernet.generate_key()

        #write the key in the file
        with open('key.txt', 'a+') as file:
            #the key is previously decoded to be written as string
            file.write(key.decode('utf-8'))

        file.close()
    

#create the credentials.txt file if it doesn't exist
def set_credentials():

    #check if the credentials file isn't already created
    if not path.exists("credentials.txt"):

        #get the encryption key instance to encrypt the credentials
        fernet = get_key_instance()
        
        #hardcoded credentials defined in code por simplicity of the task
        api_key = "1234567asdfgh"
        xe_user = "myorganization524204337"
        xe_key = "9vrb3doksi06997ieifj2n4drl"

        #encrypt the credentials
        #credentials are previously encoded to be parsed to bytes
        encrypted_api_key = fernet.encrypt(api_key.encode('utf-8'))
        encrypted_xe_user = fernet.encrypt(xe_user.encode('utf-8'))
        encrypted_xe_key = fernet.encrypt(xe_key.encode('utf-8'))

        #write the credentials in the file
        with open('credentials.txt', 'a+') as file:
            #credentials are previously decoded to be written as strings
            file.write(encrypted_api_key.decode('utf-8') + "\n")
            file.write(encrypted_xe_user.decode('utf-8') + "\n")
            file.write(encrypted_xe_key.decode('utf-8') + "\n")
        file.close()


#create the conversions.txt file if it doesn't exist
def create_conversions_file():

    #check if the file conversions.txt isn't already created
    if not path.exists("conversions.txt"):

        #create the file
        with open('conversions.txt', 'a+') as file:
            pass

        file.close()

#return the encryption key instance
def get_key_instance():
    #read the key file and get the first and unique line of the file
    with open('key.txt', 'r') as file:
        for line in file:
            #get the encryption key
            key = line
    file.close()

    #create instance of encryption with the key
    fernet = Fernet(key)

    return fernet

#get the api_key stored in the credentials file
def get_api_key_from_file():

    #read and get the first line of the file
    with open('credentials.txt', 'r') as file:
        for i, line in enumerate(file):
            if i == 0:
                encrypted_api_key = line
                break
    file.close()

    #get the encryption key instance to encrypt the credentials
    fernet = get_key_instance()
    
    #decrypt the encrypted api key
    #first api key is encoded the be parsed to bytes
    #after decryption the api key is decoded to be parsed to string
    api_key = fernet.decrypt(encrypted_api_key.encode('utf-8')).decode('utf-8')
    
    return api_key

#get the xe api username and password stored in the credentials file
def get_xe_username_and_password():

    #read and get the second and third line of the file
    with open('credentials.txt', 'r') as file:
            for i, line in enumerate(file):
                #get username
                if i == 1:
                    encrypted_username = line
                #get password
                elif i == 2:
                    encrypted_password = line
    file.close()

    #get the encryption key instance to encrypt the credentials
    fernet = get_key_instance()

    #decrypt the encrypted username and password
    #first username and password are encoded the be parsed to bytes
    #after decryption the username and password are decoded to be parsed to strings
    username = fernet.decrypt(encrypted_username.encode('utf-8')).decode('utf-8')
    password = fernet.decrypt(encrypted_password.encode('utf-8')).decode('utf-8')

    return username, password


# create the headers to make request to the xe api
def create_xe_request_headers():

    #get the username and password stored in the credentials file
    username, password = get_xe_username_and_password()

    #generate authorization token by encoding the username and password
    token = b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")

    authorization =  f'Basic {token}'

    #create the headers dictionary
    headers = {
        "authorization": authorization
    }

    return headers