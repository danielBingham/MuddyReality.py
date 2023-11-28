import os
import json

class JsonSerializable:
    def __init__(self):
        pass

    def toJson(self):
        return {} 

    def fromJson(self, data):
        return self 

class Model(JsonSerializable):
    
    def __init__(self):
        self.id = ''  

    def getId(self):
        return self.id

    def setId(self, id):
        self.id = id
        return self

    @staticmethod
    def getBasePath():
       return 'data/' 

    def getFilePath(self):
        return self.getBasePath() + self.id + '.json'

    def save(self):
        if not os.path.exists(self.getBasePath()):
            os.mkdir(self.getBasePath())

        file = open(self.getFilePath(), 'w')
        try:
            json.dump(self.toJson(), file)    
        finally:
            file.close()

        return self

    def load(self, file_path):
        file = open(file_path, 'r')
        try: 
            self.fromJson(json.load(file))
        finally:
            file.close()

        return self

class NamedModel(Model):

    def __init__(self):
        super(NamedModel, self).__init__()
        self.name = ''

    def setId(self, name):
        self.id = name
        self.name = name
        return self
