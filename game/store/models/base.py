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

    def save(self, base_path='data/'):
        if not os.path.exists(base_path):
            os.mkdir(base_path)

        filename = ''
        if isinstance(self.id, int):
            filename = base_path + str(self.id) + '.json'
        elif isinstance(self.id, str):
            filename = base_path + self.id + '.json'
        else:
            raise TypeError('Invalid id type.')

        file = open(filename, 'w')
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

    def setId(self, id):
        self.id = id
        self.name = id 
        return self
