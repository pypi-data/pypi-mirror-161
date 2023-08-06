
import json
import hashlib
from cryptography.fernet import Fernet


class item(object):

    def getName(self):
        return self.__name

    def get(self):
        return self.__data

    def setData(self, data):
        self.__data = data

    def __init__(self, data, name):
        self.__data = data
        self.__name = name

    def insertProperty(self, name, value):
        self.__data[name] = value

    def removeProperty(self, name):
        self.__data.pop(name)

    def hash(self):
        return databaseDocument.getHash(self)


class databaseDocument(object):

    def __dictKeysToList__(self, dict):
        _list = []
        for x in dict:
            try:
                for y in dict[x].get():
                    _list.append(y)
            except: 
                _list.append(x)
        return _list

    def __dictToList__(self, dict: dict):
        _list = []
        for x in dict:
            try:
                for y in dict[x].get():
                    _list.append(dict[x].get()[y])
            except: 
                _list.append(dict[x].get())
        _list.sort()
        return _list
    def __valueSearch__(self, value):
        found = False
        for x in self.__data:
            for y in self.__data[x].get():
                found =  value in self.__data[x].get()[y]
        return found
    def __doKeySearch__(self, value):
        return value in self.__dictKeysToList__(self.__data)

    def __doValueSearch__(self, value):
       # print (self.__dictToList__(self.__data))
        return value in self.__dictToList__(self.__data)

    def __init__(self, data, name):
        self.__data = data
        self.__name = name

    def insertItem(self, name: str, data: dict):
        """Inserts new item object in databaseDocument object, with given key and data"""
        self.__data[name] = item(data, name)

    def getName(self):
        """Returns databaseDocument key"""
        return self.__name

    def containsKey(self, name) -> bool:
        """Returns true if a key with given value is present in document"""
        return self.__doKeySearch__(name)

    def containsValue(self, name) -> bool:
        """Return true if a string is found in any of the documents."""
        return self.__doValueSearch__(name)

    def set(self, property, data):
        """Sets new value to key"""
        self.__data[property] = data

    def removeItem(self, property):
        """Removes property by key"""
        self.__data.pop(property)

    def get(self) -> dict:
        """Returns the contents of the databaseDocument"""
        return self.__data

    def getItem(self, name) -> item:
        """Returns item by key"""
        try:
            return self.__data[name]
        except:
            return False

    def getHash(self) -> hashlib.md5:
        return hashlib.md5((str(json.dumps(self.get(), default=databasecontroller.serialize))).encode('utf-8')).hexdigest()


class databasecontroller:
    __path = ""
    __encryptedpath = ""
    __docs = {}

    def serialize(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, databaseDocument):
            serial = obj.get()
            return serial

        if isinstance(obj, item):
            serial = obj.get()
            return serial

        return obj.__dict__

    def documentExists(self, name) -> bool:
        try:
            data = self.__docs[name]
            return True
        except:
            return False

    def getDocument(self, name: str) -> databaseDocument:
        try:
            return self.__docs[name]
        except:
            return False

    def __init__(self, path, isEncrypted):
        if(not isEncrypted):
            self.__path = path
        else:
            self.__encryptedpath = path

    def makeDatabase(self):
        if self.__path == '':
            fs = open(self.__encryptedpath, "w+")
            fs.close()
        else:
            fs = open(self.__path, "w+")
            fs.close()

    def generateDocuments(self, data):
        #ost = str(data)
        #ost = ost[2:]
        #ost = ost[:len(ost)-1]
        for x in data:
            self.__docs[x] = databaseDocument({}, x)
            try:
                for y in data[x]:
                    self.__docs[x].insertItem(y, data[x][y])
            except:
                raise Exception(
                    "Error generating items for document: " + data[x])

    def insertDocument(self, content, name):
        if(self.documentExists(name) == False):
            data = {}
            for x in content:
                data[x] = item(content[x], x)
            self.__docs[name] = databaseDocument(data, name)
        else:
            raise Exception("Error generating document: " + name +
                            ". document already exists or content couldn't be appended to instances of Item.")

    def getWhere(self, field, value) -> databaseDocument:
        try:
            for x in self.__docs:
                if(self.__docs[x].get()[field] == value):
                    return self.__docs[x]
        except:
            return False

    def decryptLoad(self, keyPath):
        try:
            with open(keyPath, 'rb') as filekey:
                key = filekey.read()
            fernet = Fernet(key)
            with open(self.__encryptedpath, 'rb') as enc_file:
                encrypted = enc_file.read()
            decrypted = fernet.decrypt(encrypted)
            if(decrypted):

                self.generateDocuments(decrypted.decode())
        except:
            raise Exception(
                "File not found or corrupted -> "+self.__encryptedpath)

    def load(self):
        try:
            fs = open(self.__path)
            data = json.loads(fs.read())
            fs.close()
            if(data):
                self.generateDocuments(data)
        except:
            raise Exception(
                "File not found or corrupted -> "+self.__path)

    def save_encrypted(self, keyPath):
        try:
            data = json.dumps(
                self.__docs, default=databasecontroller.serialize).encode()
            with open(keyPath, 'rb') as filekey:
                key = filekey.read()
            fernet = Fernet(key)
            encrypted = fernet.encrypt(data)
            with open(self.__encryptedpath, 'wb') as encrypted_file:
                encrypted_file.write(encrypted)
        except:
            raise Exception("Error saving file -> "+self.__encryptedpath)

    def generateKey(self, keypath):
        key = Fernet.generate_key()
        with open(keypath, 'wb') as filekey:
            filekey.write(key)

    def save(self):
        try:
            fs = open(self.__path, "w+")
            fs.write(json.dumps(self.__docs, default=databasecontroller.serialize))
            fs.close()
        except:
            raise Exception("Error saving file -> "+self.__path)
