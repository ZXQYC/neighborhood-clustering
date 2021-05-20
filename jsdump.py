import json

def dump_const(file,name,value):
    file.write('const %s = ' % name)
    json.dump(value, file, indent=2)
    file.write(';\n')

class Dumper:
    def __init__(self,fname):
        self.file = open(fname, 'w')
    def dump(self, name, value):
        self.file.write('const %s = ' % name)
        json.dump(value, self.file, indent=2)
        self.file.write(';\n')
    def done(self):
        self.file.close()

def json_dump(fname, value):
    file = open(fname, 'w')
    json.dump(value, file, indent=2)
    file.close()
