import os
class file:
    def __init__(self,file,filebase=8,open_=True):
        if open_==True:
            self.open=open(file,encoding='utf-8')
        self.file=file
        self.fb=self.filebase=filebase
    def read(self,file=None,line="+"):
        if file!=None:
            self.open=open(file)
        if line=="+":
            return self.open.read()
        elif line=="+line":
            return self.open.readline()
        elif line=="+lines":
            return self.open.readlines()
    def write(self,*value,sep=" ",end="\n",method=0,file=None,line="+"):
        if file!=None:
            self.file=file
        if method==0:
            if line=="+":
                return self.open.write(sep.join(value)+end)
            elif line=="+line":
                return self.open.writeline(sep.join(value))
            elif line=="+lines":
                return self.open.writelines(sep.join(value))
        elif method==1:
            return print(*value,sep=sep,end=end)
    def system(self):
        return os.system(self.file)
    def start(self):
        return os.startfile(self.file)
    def exec(self):
        return exec(self.open.read())
    def close(self):
        try:
            return self.open.close()
        except:
            pass
    def __enter__(self):
        return self
    def __exit__(self,exc_type,exc_val,exc_tb):
        self.close()
        return True
def str_import(string):
    globals()[string]=__import__(string)
class module:
    def __init__(self,m):
        self.name=m
        self.module=__import__(m)
    def has(self,value):
        return value in dir(self.module)
    def importing(self):
        str_import(self.name)
    def delvariable_module(self):
        del globals()[self.name]
    def __enter__(self):
        return self
    def __exit__(self,exc_type,exc_val,exc_tb):
        return True
class NotmoduleError(ValueError):
    pass
class NotpakegeError(NotmoduleError):
    pass
class packege(module):
    def __init__(self,p):
        try:
            __import__(p+".__init__")
        except ModuleNotFoundError as e:
            if ";" not in str(e):
                raise
            raise NotpakegeError(p+" is not packege")
    def has_module(self,value):
        try:
            if type(eval(self.name+"."+value))!=type(__import__("sys")):
                return False
            return True
        except:
            return False


            
        

