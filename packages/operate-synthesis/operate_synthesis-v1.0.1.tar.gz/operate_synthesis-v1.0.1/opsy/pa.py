'''
此模块表示对列表、字符串、数字的操作


'''
import sys
class LenError(Exception):
    '''
此错误表示序列（包括set）的长度错误
    '''
    pass    
def str_len(str1):
    '''
这个函数只能返回字符串的字符数
    '''
    if isinstance(str1,str):
        length = 0
        for c in str1:
           length = length + 1
        return length
    else:
        raise TypeError("must be str,not "+str1.__class__.__name__) 
n=""
def connect(*lt):
    '''
这个函数可以把字符串列表连接成字符串
    '''
    global n
    for i in lt:
        n=n+i
    return n            
def cm(int1,int2=1,int3=100):
    for y in range(1,int3+1):
        if y%int1==0 and y%int2==0:
            yield y
x=1
def pzy(h,l,list,sep=""):
    global x
    for i in list:
        if x%l==0:
            print(i)
            x+=1
            continue
        if i==None:
            break
        print(i,end=sep)
        x+=1
def run(function,content=None):
    if content==None:
        for f,c in function:
            return f(c)
    else:
        function(content)
def removenumber(string,Except=None):
    for i in string:
        if i.isnumeric() and i!=Except:
            string=string[:string.index(i)]+string[string.index(i)+1:]
    return string
class JCF:
    def __init__(s,start,stop=None,step=1):
        s.a=stop
        s.b=start-1
        if stop==None:
            s.a=start
            s.b=-1
    def __iter__(s):
        return s
    def __next__(s):
        if s.b>=s.a-1:
            raise StopIteration()
        else:
            s.b+=1
            return (s.b+s.b,s.b*s.b,s.b**s.b)
def jcf(start,stop=None,step=1):
    a=stop
    b=start
    if stop==None:
        a=start
        b=0
    while True:
        if b>=a:
            raise StopIteration()
        else:
            yield (b+b,b*b,b**b)
            b+=step
i=0
a_=[]
a=set()
def conversiontype_empty(value=None,Type=int):
    if value in (0,False,0.0,None,"",(),[],{},set(),frozenset()):
        if Type==str:
            return ""
        try:
            iter(Type(()))
            return Type(())
        except TypeError:
            if Type==int:
                return 0
    else:
        raise ValueError("The content must be empty")
contype_empty=conversiontype_empty
def randrandom(*contend,repeat=False,Type=int):
    '''
此函数会生成一个随机序列，每次调用这个函数都会返回其中的元素，如果repeat成立，
随机数则会重复，否则不会重复，而Type是返回值的类型
源码：
def randrandom(*contend,repeat=False,Type=int):
    try:
        assert len(contend)==2,"contend's len must be 2"
    except AssertionError as error:
        e=(lambda a:a)(error)
        raise LenError(error)
    finally:
        if type(Type)!=type:
            raise TypeError(f"msut be type,not {type(Type).__name__}")
        global a_
        global i
        if i==0 or len(a_)==0:
            a_=list(map(str,list(range(contend[0],contend[1]))))
        global a
        if repeat or len(a)==0:
            if i>0:
                a_.reverse()
            a=set(a_)
        a_.append(a_.pop())
        b=a.pop()
        a.add(b)
    i+=1
    return Type(int(b))
    '''
    try:
        assert len(contend)==2,"contend's len must be 2"
    except AssertionError as error:
        e=(lambda a:a)(error)
        raise LenError(error)
    finally:
        if type(Type)!=type:
            raise TypeError(f"msut be type,not {type(Type).__name__}")
        global a_
        global i
        if i==0 or len(a_)==0:
            a_=list(map(str,list(range(contend[0],contend[1]))))
        global a
        if repeat or len(a)==0:
            if i>0:
                a_.reverse()
            a=set(a_)
        a_.append(a_.pop())
        b=a.pop()
        a.add(b)
    i+=1
    return Type(int(b))
def drange(start,stop,step):
    r = start
    while r < stop:
        yield float("%g"%r)
        r += step
def sinrourobfor(num):
    return num*(num-1)//2
srrf=sinrourobfor
def fractional_digits(float_):
    returner=len(str(float_).split(".")[1])
    return(returner)    
def base_decimal(integer,base):
    if base not in range(2,11):
        raise ValueError("base must be in range(2,11)")
    if type(integer) not in (int,bool):
        raise TypeError("integer's type must be int or bool,not "+type(integer).__name__)
    if type(base) not in (int,):
        raise TypeError("base's type must be int,not "+type(base).__name__)
    returner=[]
    while not integer==0:
        returner+=[str(integer%base)];integer//=base
    returner.reverse()
    return float(f"{base}.{''.join(returner)}")
def str_import(string):
    globals()[string]=__import__(string)
import sys
def eval_input(value):
    '''
类似于python2的input
'''
    return eval(input(str(value)))

def notenter_input(value,print_end="\n"):
    '''
按下Ctrl+D完结输入
'''
    print(value,end=print_end)
    return sys.stdin.read()
def notenter_input_list(value,print_end="\n"):
    print(value,end=print_end)
    return sys.stdin.readlines()
ne_i_l=notenter_input_list
def easy_str(*values):
    '''
可以让某些字符串不用引号
'''
    for i in values:
        globals()[i]=i
class easylist(object):
    '''
升级版list，在list的基础上加了一些功能
'''
    #初始化
    def __init__(self,value=()):
        self.value=list(value)
        self.n=-1
    def __call__(self,start=None,stop=None,step=1,Type=int):
        '''
切片与取值1
'''
        if stop==None and Type==int:
            return self.value[start]
        elif stop==None and Type==slice:
            stop=start
            start=0
        elif start==None and stop==None and Type==slice:
            start=0
            stop=len(self)
        elif Type not in (int,slice):
             raise ValueError("Type must be int or slice")
        return easylist(self.value[start:stop:step])
    #返回值
    def __str__(self):
        return f"to_easylist{tuple(self.value)}"
    def __iter__(self):
        '''
自身就是容器
'''
        return self
    def __next__(self):
        '''
本身就能next()
'''
        self.n+=1
        if self.n>=len(self.value):
            raise StopIteration()
        return self.value[self.n]
    #值与格式化
    def __getitem__(self, index):
        '''
切片与取值2
'''
        if isinstance(index, slice):
            return str(easylist(self.value[index]))
        return self.value[index]
    def __format__(self,r):
        '''
新格式化
'''
        if r=="":
            return str(self)
        c=r
        if "str" in c:

            c=c.replace("str",str(choice(self.value)))
        elif "repr" in c:

            c=c.replace("repr",repr(choice(self.value)))
        elif "list" in c:

            c=c.replace("list",str(list(str(choice(self.value)))))
        elif "tuple" in c:

            c=c.replace("tuple",str(tuple(str(choice(self.value)))))
        else:
            c=self[eval(r)]

        return c
    def __setitem__(self, index, value):
        '''
赋值
'''
        self.value[index] = value
    def __delitem__(self, key):
        '''
删除值
'''
        del self.value[key]
    #运算符
    def __add__(self,other):
        return easylist(list(self)+list(other))
    def __mul__(self,other):
        return easylist(list(self)*int(other))
    def __mod__(self, other):
        modlist=[]
        if type(other)==type:
            for i in self:    
                if type(i)==other:
                    modlist+=[i]
        else:
            for i in self:    
                if i not in other:
                    modlist+=[i]
        return easylist(modlist)
    def __len__(self):
        return self.value.__len__()
    #内置函数
    def index(s,va):
        return s.value.index(va)
    def append(s,va):
        return s.value.append(s)
    def extend(s,va):
        return s.value.extend(va)
    def pop(s,idx):
        return s.value.pop(idx)
    def remove(s,va):
        return s.value.remove(va)
    def count(s,va):
        return s.value.count(va)
    def all(s,value=None):
        if value is not None:
            return s.count(value)==len(s)
        else:
            return len(set(s))==1
    def copy(s):
        return s[:]
    def reverse(s):
        return s.value.reverse()
    def sort(s,reverse=False,key=None):
        return s.value.sort(reverse=reverse,key=key)
def to_easylist(*args):
    return easylist(args)
class canwith:
    def __init__(self,value):
        self.value=value
    def __enter__(self):
        return self.value
    def __exit__(self,a,b,c):
        return True
def output(*value,sep=' ',end='\n',file=sys.stdout,flush=False):
    print(*(tuple(map(repr,value))),sep=sep,end=end,file=file,flush=flush)
def notcallable(value):
    return value()
def fcanwith(f):
    f=f
    class A:
        try:
            def __init__(self,*args,**kwargs):
                self.values=args
                self.kwvalues=kwargs
            def __enter__(self):
                return list(f(*(self.values),**(self.kwvalues)))[0]
            def __exit__(self,a,b,c):
                return True
        except NameError:
            pass
    A.f=f
    return A
class mutable_str(str):
    '''
可变字符串
'''
    def __init__(self,bytes_or_buffer,encoding=None,errors=None):
        if (encoding is None) and (errors is None):
            self.string=str(bytes_or_buffer)
            self.seq=list(self.string)
        else:
            self.string=str(bytes_or_buffer,encoding,errors)
            self.seq=list(self.string)
    def __str__(self):
        return f"mutable_str({repr(''.join(self.seq))})"
    def __getitem__(self,idx):
        return self.str_()[idx]
    def __setitem__(self,idx,value):
        if isinstance(idx,slice):
            self.seq[idx]=list(value)
        else:
            self.seq[idx]=value
        self.flush_string()
    def __delitem__(self,idx):
        del self.seq[idx]
        self.flush_string()
    def flush_string(self):
        self.string=self.str_()
    def str_(self):
        return ''.join(self.seq)
    def append(self,obj,flush=True):
        self.seq.append(obj)
        if flush:
            self.flush_string()
    def extend(self,objs,flush=True):
        self.seq.extend(list(objs))
        if flush:
            self.flush_string()
    def pop(self,idx,flush=True):
        r=self.seq.pop(idx)
        if flush:
            self.flush_string()
        return r
    def remove(self,value,flush=True):
        self.seq.remove(value)
        if flush:
            self.flush_string()
    def clear(self,flush=True):
        self.seq.clear()
        if flush:
            self.flush_string()
    def insert(self,idx,obj,flush=True):
        self.seq.insert(idx,obj)
        if flush:
            self.flush_string()
    def reverse(self,flush=True):
        self.seq.reverse()
        if flush:
            self.flush_string()
    def sort(key=None,reverse=False,flush=True):
        self.seq.sort(key=key,reverse=reverse)
        if flush:
            self.flush_string()
if __name__=='__main__':
    print(str_len("6666rfce"))
    print(connect("1","2","3","4","5","6"))
    pzy(3,2,("1","2","3","4","5","6"))
    print(list(cm(2,3,50)))
    run(eval,("print(\"go\")"))
    print(list(JCF(11)))
    print(list(jcf(11)))
    for i in range(15):
        print(tuple(randrandom(1,15,Type=range)))
    print(list(drange(0,1,0.1)))
    print(sinrourobfor(10))
    print(srrf(10))
    print(fractional_digits(3.345))
    print(base_decimal(189,4))
    easy_str("g","7","__9")
    a=easylist("dfei09")
    b=to_easylist(6,1,5,9)
    print(b)
    print(a)
    print(a[0:3])
    print(a(0,3,Type=slice))
    output("b")
    with canwith("r") as a:
        print(a)
    @fcanwith
    def a(b,c=1):
        return [b+c]
    with a(3,c=4) as b:
        print(b)
    e=mutable_str(546)
    e.append("7")
    e.flush_string()
    print(e.pop(2))
    e[0]="g"
    print(e.string)
    del e[1]
    print(e.string)
