from math import *
import cmath
'''
Please don't change the below mentioned values of {errors} and {name}
without reading the whole code.It might result in code ambiguity.
##version==0.0.7##
'''
negative_error ="Sides can't be less than or equal to zero"
no_of_side_error="Number of sides can't be float"
name="py_math_help"

class triangle:
    def area(a,b,c=None):
        if c==None:
            if not(a>0 and b>0):
                raise ValueError( negative_error)
            return 1/2*a*b
        else:
            if not(a>0 and b>0 and c>0):
                raise ValueError( negative_error)
            if a+b>c and b+c>a and c+a>b:
                s=(a+b+c)/2
                ar=s*(s-a)*(s-b)*(s-c)
                return sqrt(ar)
        
    def perimeter(a,b,c):
        if not(a>0 and b>0 and c>0):
            raise ValueError( negative_error)
        return a+b+c

class quadilateral:
    def __init__(self,name) -> None:
        self.name=name

    def area(self,a,b=None):
        if self.name=="square" and a>0 and b!=None:
            raise ValueError("Square accepts only one argumnet")          
        if self.name=="square" and a>0 and b==None:
            return a*a
        try:    
            if not(a>0 and b>0):
                raise ValueError( negative_error)
            return a*b
        except:
            raise TypeError("Arguent Error")    

    def perimeter(self,a,b=None):
        if self.name=="square" and a>0 and b!=None:
            raise ValueError("Square accepts only one argumnet")  
        if self.name=="square" and a>0 and b==None:
            return 4*a               
        try:    
            if not(a>0 and b>0):
                raise ValueError( negative_error)
            return 2*(a+b)
        except:
            raise TypeError("Arguent Error")        

rectangle=quadilateral("rectangle")
square=quadilateral("square")

class quadilateral1:
    def __init__(self,name) -> None:
        self.name=name

    def area(self,d1,d2):
        if not(d1>0 and d2>0):
            raise ValueError(negative_error)
        return (1/2)*d1*d2    

    def perimeter(self,side1,side2=None):
        if self.name=="rhombus" and side2==None and side1>0:
            return 4*side1
        elif self.name=="parallelogram" and side1>0 and side2>0:
            return 2*(side1+side2)
        else:
            raise TypeError("Argument error")

rhombus=quadilateral1("rhombus")
parallelogram=quadilateral1("parallelogram")

def table(a):
    ta=""
    for i in range(1,11):
        ta=ta+f'{a}*{i}={a*i}\n'
    return ta

class polygon:
  def area(side,len):
    if not(side>2 and len>0):
        raise ValueError("Argument error")
    if not (isinstance(side,int)):
        raise TypeError( no_of_side_error)
    return float('%.5f'%((side*len*len)/(4*tan(pi/side))))

  def perimeter(side,len):
    if not(side>2 and len>0):
        raise ValueError("Argument error")
    if not (isinstance(side,int)):
        raise TypeError( no_of_side_error)      
    return side*len

class circle:
    def area(r):
        if not(r>0):
            raise ValueError( negative_error)

    def perimeter(r):
        if not(r>0):
            raise ValueError( negative_error)

def query(arg,input_string): 
    count=0
    for i in input_string.split(" "):
        if i.lower()==arg:
            count+=1
    if count>0:
        return True
    else:
        return False 

def query1(lst,a):                                    
        if query("area",a) and query("perimeter",a) :
            for i in lst:
                print(l[i][6:])
        elif query("perimeter",a):
            print(l[lst[1]][6:])
        elif query("area",a) :
            print(l[lst[0]][6:])
        else:
            for i in lst:
                print(l[i][6:])  

def query2(lst,a):
        if query("volume",a) and (query("csa",a) or query("curved",a)) and (query("tsa",a) or query("total",a)):
            for i in lst:
                print(l[i][6:])
        elif query("tsa",a) or query("total",a):
            print(l[lst[0]][6:])
        elif query("csa",a) or query("curved",a):
            print(l[lst[1]][6:])
        elif query("volume",a):
            print(l[lst[2]][6:]) 
        else:
            for i in lst:
                print(l[i][6:]) 

class three_d1:
    def __init__(self,name) -> None:
        self.name=name

    def CSA(self,a):
        if not(a>0):
            raise ValueError(negative_error)
        if self.name=="cube":
            return 4*a*a
        elif self.name=="sphere":
            return 4*pi*a*a
        elif self.name=="hemisphere":
            return 2*pi*a*a  
    def TSA(self,a):
        if not(a>0):
            raise ValueError(negative_error)
        if self.name=="cube":
            return 6*a*a
        elif self.name=="sphere":
            return 4*pi*a*a
        elif self.name=="hemisphere":
            return 3*pi*a*a 
    def volume(self,a):
        if not(a>0):
            raise ValueError(negative_error)
        if self.name=="cube":
            return a*a*a
        elif self.name=="sphere":
            return (4/3)*pi*a*a*a
        elif self.name=="hemisphere":
            return (2/3)*pi*a*a*a 

cube=three_d1("cube")
sphere=three_d1("shpere")
hemisphere=three_d1("hemisphere")

class three_d2:
    def __init__(self,name) -> None:
        self.name=name

    def CSA(self,r,h):
        if not(r>0 and h>0):        
            raise ValueError(negative_error)
        if self.name=="cylinder":
            return 2*pi*r*h
        elif self.name=="cone":
            return pi*r*h

    def TSA(self,r,h):
        if not(r>0 and h>0):
            raise ValueError(negative_error)
        if self.name=="cylinder":
            return 2*pi*r*(r+h)
        elif self.name=="cone":
            return pi*r*(h+r)
 
    def volume(self,r,h):
        if not(r>0 and h>0):
            raise ValueError(negative_error)
        if self.name=="cylinder":
            return pi*r*r*h
        elif self.name=="cone":
            return (1/3)*pi*r*r*h
  
cone=three_d2("cone")
cylinder=three_d2("cylinder")
  
class cuboid:
    def TSA(a,b,c):
        if not(a>0 and b>0 and c>0):
            raise ValueError( negative_error)
        return 2*(a*b+b*c+c*a)
    def CSA(a,b,c):
        if not(a>0 and b>0 and c>0):
            raise ValueError( negative_error)        
        return 2*c*(a+b)
    def volume(a,b,c):
        if not(a>0 and b>0 and c>0):
            raise ValueError( negative_error) 
        return a*b*c  

def slant_height(r,h):
    return (sqrt(r*r+h*h))

def query3(control,lst,a):
        if (query("binary",a) and (control !="binary")):
            print(l[lst[0]])
        elif (query("decimal",a) and (control !="decimal")):
            print(l[lst[1]])
        elif query("octal",a) and control!="octal":
            print(l[lst[2]])
        elif query("hexadecimal",a) and control!="hexadecimal":
            print(l[lst[3]])
        else:
            for i in lst:
                print(l[i])

def factorial(x,y=None):
    if (x==0 or x==1) and y==None:
        return 1
    elif isinstance(x,int) and x>0 and y==None:
        fact=1
        for i in range(1,x+1):
            fact=fact*i
        return fact
    elif x>0 and y>0 and y>x:  
        for i in range(int(x),int(y) + 1):
            fact = 1
            for j in range(1, i + 1):
                fact = fact * j
            print(f'The factorial of {i} is {fact}')
    else:
        raise ValueError("Invalid Argument Passed Into Function")   

def prime(x,y=None):
    if (x==0 or x==1)and y==None:
        return False
    elif x>1 and y==None:
        flag=0
        for i in range(2,int(sqrt(x))+1):
            if(x%i==0):
                flag=1
                break
        if flag==1:
            return False
        else:
            return True        
    elif x>=0 and y>0 and y>x:
        primes=[]
        for i in range(int(x),int(y)):
            if i==0 or i==1:
                continue
            else:
                flag=0
                for j in range(2,int(sqrt(i))+1):
                    if(i%j==0):
                        flag=1
                        break
                if flag==0:
                    primes.append(i)    
        return primes      
    else:
        return False                  

def isPerfectSquare(x):
    s = int(sqrt(x))
    return s*s == x

def isfib(x,y=None):
    if x>0 and y==None:
        return isPerfectSquare(5*x*x + 4) or isPerfectSquare(5*x*x - 4)
    elif x>0 and y>0 and y>x:
        fib=[]
        for i in range(int(x),int(y)):
            if isPerfectSquare(5*i*i + 4) or isPerfectSquare(5*i*i - 4):
                fib.append(i)
        return fib        
    else:
        return False      

def palindrome(x):
    if x[::-1] == x:
        return True
    return False

def factors(x):
    factor=[]
    for i in range(1,x+1):
        if x%i==0:
            factor.append(i)
    return factor            

def isleap(year,years=None):
    if isinstance(year,int) and year>0 and years==None:
        leap=False
        if(True):
            if(year%100==0 and year%400==0 and year%4==0):
                leap=True
            if(year%4==0 and year%100!=0):
                leap=True
        return leap
    elif year>0 and years>0 and years>year:
        leap=[]
        for i in range(int(year),int(years)):
            if(True):
                if(i%100==0 and i%400==0 and i%4==0):
                    leap.append(i)
                if(i%4==0 and i%100!=0):
                    leap.append(i)        
        return leap            
    else:
        raise ValueError("Invalid input in Argument feild")

def isarmstrong(x,y=None):
    if isinstance(x,int) and x>0 and y==None: 
        order=len(str(x))
        sum=0;temp=x
        while temp > 0:
            digit = temp % 10
            sum += digit ** order
            temp //= 10 
        if x==sum:
            return True
        return False      
    elif x>0 and y>0 and y>x:
        arms=[]
        for i in range(int(x),int(y)):
            order=len(str(i))
            sum=0;temp=i
            while temp > 0:
                digit = temp % 10
                sum += digit ** order
                temp //= 10    
            if i==sum:
                arms.append(i)
        return arms
    else:
        raise ValueError("Invalid input in Argument feild")

def hcf(x, y):
    h=0
    if x > y:
        smaller = y
    else:
        smaller = x
    for i in range(1, smaller+1):
        if((x % i == 0) and (y % i == 0)):
            h = i 
    return h

class converter:
    def __init__(self,name,value) -> None:
        self.name=name
        self.value=value

    def validate(self):
        if self.name=="binary":
            if not(isinstance(self.value,int) and self.value>=0) :
                raise ValueError("Invalid Argument")
            var=str(self.value)    
            for i in var:
                if not(i=='0' or i=='1'):
                    raise ValueError("Invalid argument")          

        elif self.name=="decimal":
            if not(isinstance(self.value,int) and self.value>=0) :
                raise ValueError("Invalid Argument")

        elif self.name=="octal":
            if not(isinstance(self.value,int) and self.value>=0) :
                raise ValueError("Invalid Argument")
            for i in str(self.value):
                if not(int(i)<8):
                    raise ValueError("Invalid argument")

        elif self.name=="hexadecimal":
            if not(isinstance(self.value,str)and('-' not in self.value)and('.' not in self.value)and len(self.value)!=0):
                raise ValueError("Invalid Argument")
        xam=["a","b","c","d","e","f","A","B","C","D","E","F"]
        for i in str(self.value):
            if not(i.isnumeric() or i in xam ):
                raise ValueError("Invalid argumnet")  

    def bin_to_dec(b):
        bin=converter("binary",b)
        bin.validate()
        b=str(b)
        s = 0
        j = len(b)
        for i in b:
            s = s+int(i)*2**(j-1)
            j -= 1
        return s

    def bin_to_oct(b):
        bin=converter("binary",b)
        bin.validate()        
        d=converter.bin_to_dec(b)
        return converter.dec_to_oct(d)

    def bin_to_hex(b):
        bin=converter("binary",b)
        bin.validate()         
        d=converter.bin_to_dec(b)
        return converter.dec_to_hex(d)

    def dec_to_oct(d):  
        dec=converter("decimal",d)
        dec.validate() 
        s = ''
        while True:
            t = d % 8
            s = s+str(t)
            d = d//8
            if d >= 8:
                pass
            else:
                s = s+str(d)
                break
        o = s[::-1]
        return int(o)

    def dec_to_hex(d):  
        dec=converter("decimal",d)
        dec.validate()       
        a = d
        s = ''
        while True:
            t = a % 16
            if t == 10:
                s = s+'A'
            elif t == 11:
                s = s+'B'
            elif t == 12:
                s = s+'C'
            elif t == 13:
                s = s+'D'
            elif t == 14:
                s = s+'E'
            elif t == 15:
                s = s+'F'
            else:
                s = s+str(t)
            a = a//16
            if a >= 16:
                pass
            else:
                if a == 10:
                    s = s+'A'
                elif a == 11:
                    s = s+'B'
                elif a == 12:
                    s = s+'C'
                elif a == 13:
                    s = s+'D'
                elif a == 14:
                    s = s+'E'
                elif a == 15:
                    s = s+'F'
                else:
                    s = s+str(a)
                    break
        h = s[::-1]
        return h

    def dec_to_bin(d):
        dec=converter("decimal",d)
        dec.validate()        
        if d==0:
            return 0
        i = 0
        str = ""
        while True:
            if 2**i < d:
                i += 1
                pass
            else:
                break
        count = i
        for j in range(0, i+1):
            if d-2**(count) >= 0:
                d = d-2**(count)
                str = str+'1'
                count = count-1
            else:
                str = str+'0'
                count = count-1
        if str[0] == '0':
            b = str[1:len(str)]
            return int(b)
        else:
            b = str
            return int(b)

    def oct_to_dec(o): 
        oct=converter("octal",o)
        oct.validate()      
        o=str(o)
        d = 0
        j = len(o)
        for i in o:
            d = d+int(i)*8**(j-1)
            j -= 1
        return d

    def oct_to_bin(o):
        oct=converter("octal",o)
        oct.validate()  
        d=converter.oct_to_dec(o)
        return converter.dec_to_bin(d)

    def oct_to_hex(o):
        oct=converter("octal",o)
        oct.validate()        
        d=converter.oct_to_dec(o)
        return converter.dec_to_hex(d)

    def hex_to_bin(h):
        hex=converter("hexadecimal",h)
        hex.validate()        
        d=converter.hex_to_dec(h)
        return converter.dec_to_bin(d)

    def hex_to_oct(h):
        hex=converter("hexadecimal",h)
        hex.validate()         
        d=converter.hex_to_dec(h)
        return converter.dec_to_oct(d)

    def hex_to_dec(h):  
        hex=converter("hexadecimal",h)
        hex.validate()
        s = 0
        j = len(h)
        for i in h:
            if i == 'a' or i == 'A':
                i = 10
                s = s+i*16**(j-1)
                j -= 1
            elif i == 'b' or i == 'B':
                i = 11
                s = s+i*16**(j-1)
                j -= 1
            elif i == 'c' or i == 'C':
                i = 12
                s = s+i*16**(j-1)
                j -= 1
            elif i == 'd' or i == 'D':
                i = 13
                s = s+i*16**(j-1)
                j -= 1
            elif i == 'e' or i == 'E':
                i = 14
                s = s+i*16**(j-1)
                j -= 1
            elif i == 'f' or i == 'F':
                i = 15
                s = s+i*16**(j-1)
                j -= 1
            else:
                s = s+int(i)*16**(j-1)
                j -= 1
        return s        

def quadratic(a=0,b=0,c=0):
    if a==0:
        return -c/b
    r1=(-1*b+cmath.sqrt(b*b-4*a*c))/2*a
    r2=(-1*b-cmath.sqrt(b*b-4*a*c))/2*a
    if r1.imag==0 :
        return [r1.real,r2.real]
    else:
        return [r1,r2] 

def cubic(a=0, b=0, c=0, d=0):
    if (a==0 and b==0 and c==0 and d==0):
        return [0.0,0.0,0.0]
    elif (a == 0 and b == 0):                     
        return ([(-d * 1.0) / c])                 
    elif (a == 0):                              
        return quadratic(b,c,d)
    f = findF(a, b, c)                          
    g = findG(a, b, c, d)                       
    h = findH(g, f)                             
    if f == 0 and g == 0 and h == 0:            
        if (d / a) >= 0:
            x = (d / (1.0 * a)) ** (1 / 3.0) * -1
        else:
            x = (-d / (1.0 * a)) ** (1 / 3.0)
        return  ([float('%.5f'%x), float('%.5f'%x), float('%.5f'%x)])         
    elif h <= 0:                              
        i = sqrt(((g ** 2.0) / 4.0) - h)   
        j = i ** (1 / 3.0)                 
        k = acos(-(g / (2 * i)))           
        L = j * -1                         
        M = cos(k / 3.0)                   
        N = sqrt(3) * sin(k / 3.0)    
        P = (b / (3.0 * a)) * -1                
        x1 = 2 * j * cos(k / 3.0) - (b / (3.0 * a))
        x2 = L * (M + N) + P
        x3 = L * (M - N) + P
        return ([float('%.5f'%x1), float('%.5f'%x2), float('%.5f'%x3)])           
    elif h > 0:                                 
        R = -(g / 2.0) + sqrt(h)           
        if R >= 0:
            S = R ** (1 / 3.0)                  
        else:
            S = (-R) ** (1 / 3.0) * -1          
        T = -(g / 2.0) - sqrt(h)
        if T >= 0:
            U = (T ** (1 / 3.0))                
        else:
            U = ((-T) ** (1 / 3.0)) * -1        
        x1 = (S + U) - (b / (3.0 * a))
        x2 = -(S + U) / 2 - (b / (3.0 * a)) + (S - U) * sqrt(3) * 0.5j
        x3 = -(S + U) / 2 - (b / (3.0 * a)) - (S - U) * sqrt(3) * 0.5j
        return [x1, x2, x3]       
def findF(a, b, c):
    return ((3.0 * c / a) - ((b ** 2.0) / (a ** 2.0))) / 3.0
def findG(a, b, c, d):
    return (((2.0 * (b ** 3.0)) / (a ** 3.0)) - ((9.0 * b * c) / (a **2.0)) + (27.0 * d / a)) /27.0
def findH(g, f):
    return ((g ** 2.0) / 4.0 + (f ** 3.0) / 27.0)
    
###########################################################################################################################################            
l=['',
  f'1.    AREA OF TRIANGLE \n Syntax -> {name}.triangle.area(<length>,<bredth>)\n Syntax -> {name}.triangle.area(<side1>,<side2>,<side3>)',
  f'2.    PERIMETER OF TRIANGLE \n Syntax -> {name}.triangle.perimeter(<side1>,<side2>,<side3>)',
  f'3.    AREA OF SQUARE \n Syntax -> {name}.square.area(<side>)',
  f'4.    PERIMETER OF SQUARE \n Syntax -> {name}.square.perimeter(<side>)',
  f'5.    AREA OF rectangle \n Syntax -> {name}.rectangle.area(<side_1>,<side_2>)',
  f'6.    PERIMETER OF rectangle \n Syntax -> {name}.rectangle.perimeter(<side_1>,<side_2>)',
  f'7.    AREA OF polygon \n Syntax -> {name}.polygon.area(<no_of_sides>,<length>)',
  f'8.    PERIMETER OF polygon \n Syntax -> {name}.polygon.perimeter(<no_of_sides>,<length>)',
  f'9.    PRINT TABLE OF A NUMBER \n Syntax -> print({name}.table(<number>))',
  f'10.   TOTAL SURFACE AREA OF cube \n Syntax -> {name}.cube.TSA(<length>)',
  f'11.   CURVED SURFACE AREA OF cube \n Syntax -> {name}.cube.CSA(<length>)',
  f'12.   VOLUME OF cube \n Syntax -> {name}.cube.volume(<length>)',
  f'13.   TOTAL SURFACE AREA OF cuboid \n Syntax -> {name}.cuboid.TSA(<length>,<bredth>,<height>)',
  f'14.   CURVED SURFACE AREA OF cuboid \n Syntax -> {name}.cuboid.CSA(<length>,<bredth>,<height>)',
  f'15.   VOLUME OF cuboid \n Syntax -> {name}.cuboid.volume(<length>,<bredth>,<height>)',
  f'16.   TOTAL SURFACE AREA OF sphere \n Syntax -> {name}.sphere.CSA(<radius>)',
  f'17.   CURVED SURFACE AREA OF sphere \n Syntax -> {name}.sphere.CSA(<radius>)',
  f'18.   VOLUME OF sphere \n Syntax -> {name}.sphere.volume(<radius>)',    
  f'19.   TOTAL SURFACE AREA OF hemisphere \n Syntax -> {name}.hemisphere.TSA(<radius>)',
  f'20.   CURVED SURFACE AREA OF hemisphere \n Syntax -> {name}.hemisphere.CSA(<radius>)',
  f'21.   VOLUME OF hemisphere \n Syntax -> {name}.hemisphere.volume(<radius>)', 
  f'22.   TOTAL SURFACE AREA OF cylinder \n Syntax -> {name}.cylinder.TSA(<radius>,<height>)',
  f'23.   CURVED SURFACE AREA OF cylinder \n Syntax -> {name}.cylinder.CSA(<radius>,<height>)',
  f'24.   VOLUME OF cylinder \n Syntax -> {name}.cylinder.volume(<radius>,<height>)',  
  f'25.   TOTAL SURFACE AREA OF cone \n Syntax -> {name}.cone.TSA(<radius>,<slant_height>)',
  f'26.   CURVED SURFACE AREA OF cone \n Syntax -> {name}.cone.CSA(<radius>,<slant_height>)',
  f'27.   VOLUME OF cone \n Syntax -> {name}.cone.volume(<radius>,<height>)', 
  f'28.   SLANT HEIGHT OF cone \n Syntax -> {name}.slant_height(<radius>,<height>)', 
  f'29.   AREA OF circle \n Syntax -> {name}.circle.area(<radius>)',
  f'30.   PERIMETER OF circle \n Syntax -> {name}.circle.perimeter(<radius>)', 
  f'31.   AREA OF parallelogram \n Syntax -> {name}.parallelogram.area(<digonal_1>,<digonal_2>)',
  f'32.   PERIMETER OF parallelogram \n Syntax -> {name}.parallelogram.perimeter(<side_1>,<side_2>)', 
  f'33.   CONVERT BINARY TO DECIMAL \n Syntax -> {name}.converter.bin_to_dec(<binary_number>)',   
  f'34.   CONVERT BINARY TO OCTAL \n Syntax -> {name}.converter.bin_to_oct(<binary_number>)',   
  f'35.   CONVERT BINARY TO HEXADECIMAL \n Syntax -> {name}.converter.bin_to_hex(<binary_number>)',   
  f'36.   CONVERT DECIMAL TO BINARY \n Syntax -> {name}.converter.dec_to_bin(<decimal_number>)',   
  f'37.   CONVERT DECIMAL TO OCTAL \n Syntax -> {name}.converter.dec_to_oct(<decimal_number>)',  
  f'38.   CONVERT DECIMAL TO HEXADECIMAL \n Syntax -> {name}.converter.dec_to_hex(<decimal_number>)',  
  f'39.   CONVERT OCTAL TO BINARY \n Syntax -> {name}.converter.oct_to_bin(<octal_number>)',   
  f'40.   CONVERT OCTAL TO DECIMAL \n Syntax -> {name}.converter.oct_to_dec(<octal_number>)',  
  f'41.   CONVERT OCTAL TO HEXADECIMAL \n Syntax -> {name}.converter.oct_to_hex(<octal_number>)',  
  f'42.   CONVERT HEXADECIMAL TO BINARY \n Syntax -> {name}.converter.hex_to_bin("<hexadecimal_number>")',   
  f'43.   CONVERT HEXADECIMAL TO DECIMAL \n Syntax -> {name}.converter.hex_to_dec("<hexadecimal_number>")',   
  f'44.   CONVERT HEXADECIMAL TO OCTAL \n Syntax -> {name}.converter.hex_to_oct("<hexadecimal_number>")',
  f'45.   AREA OF rhombus \n Syntax -> {name}.rhombus.area(<digonal_1>,<digonal_2>)',
  f'46.   PERIMETER OF rhombus \n Syntax -> {name}.rhombus.perimeter(<side>)',
  f'47.   FACTORIAL OF A NUMBER \n Syntax -> {name}.factorial(<number>)',     
  f'48.   FACTORIAL OF NUMBERS IN RANGE \n Syntax -> {name}.factorial(<beginning>,<end>)',
  f'49.   CHECK WHETHER A NUMBER IS PRIME \n Syntax -> {name}.prime(<number>)',     
  f'50.   PRIME NUMBERS IN GIVEN RANGE\n Syntax -> {name}.prime(<beginning>,<end>)',   
  f'51.   CHECK WHETHER A NUMBER IS A FIBONACCI NUMBER \n Syntax -> {name}.isfib(<number>)',     
  f'52.   FIBONACCI NUMBERS IN GIVEN RANGE\n Syntax -> {name}.isfib(<beginning>,<end>)',
  f'53.   CHECK WHETHER A STRING IS PALINDROME \n Syntax -> {name}.palindrome(<input_string>)',
  f'54.   FACTORS OF A GIVEN NUMBER \n Syntax -> {name}.factors(<number>)',
  f'55.   CHECK WHETHER A YEAR IS LEAP YEAR \n Syntax -> {name}.isleap(<year>)',     
  f'56.   LEAP YEARS IN GIVEN RANGE\n Syntax -> {name}.isleap(<beginning>,<end>)',  
  f'57.   CHECK WHETHER A NUMBER IS AN ARMSTRONG NUMBER \n Syntax -> {name}.isarmstrong(<number>)',     
  f'58.   ARMSTRONG NUMBERS IN A GIVEN RANGE \n Syntax -> {name}.isarmstrong(<beginning>,<end>)',
  f'59.   FIND HCF OF TWO NUMBERS \n Syntax -> {name}.hcf(<number_1>,<number_2>)',
  f'60.   ROOTS OF A QUADRATIC EQUATION (ax**2+bx+c=0) \n Synatx -> {name}.quadratic(a,b,c)', 
  f'61.   ROOTS OF A CUBIC EQUATION (ax**3+bx**2+cx+d=0) \n Synatx -> {name}.cubic(a,b,c,d)'               
  ]
###########################################################################################################################################            

def help():
    print("***********************************************************************************************")
    print()
    print("This module has been developed by Harsh Gupta.")
    print()
    print("To view all the functions with corresponding Syntax Type:\n >>>py_math_help.index()")
    print("To search a specific problem... Type:\n >>>py_math_help.search('<your problem'>)")
    print("  For example: \n >>>py_math_help.search('volume of cuboid') \n >>>py_math_help.search('convert binary to decimal') \n >>>py_math_help.search('table of 10')")
    print()
    print("***********************************************************************************************")

def index():
    for i in l:
        print(i)           

def search(a):
    if query("triangle",a):
        query1([1,2],a)           
    if query("square",a):
        query1([3,4],a)
    if query("rectangle",a):
        query1([5,6],a)
    if query("polygon",a):
        query1([7,8],a)        
    if query("table",a):
        print(l[9][6:])
    if query("cube",a):
        query2([10,11,12],a)   
    if query("cuboid",a):
        query2([13,14,15],a)
    if query("sphere",a):
        query2([16,17,18],a)
    if query("hemisphere",a):
        query2([19,20,21],a)  
    if query("cylinder",a):
        query2([22,23,24],a)
    if query("cone",a):
        query2([25,26,27],a) 
    if query("slant",a):
        print(l[28][6:])      
    if query("circle",a):
        query1([29,30],a)
    if query("parallelogram",a):
        query1([31,32],a)     
    if query("binary",a):
        query3("binary",[0,33,34,35],a)            
    if query("decimal",a):
        query3("decimal",[36,0,37,38],a)  
    if query("octal",a):
        query3("octal",[39,40,0,41],a)         
    if query("hexadecimal",a):
        query3("hexadecimal",[42,43,44,0],a)  
    if query("rhombus",a):
        query1([45,46],a)      
    if query("factorial",a):
        print(l[47][6:])
        print(l[48][6:])        
    if query("prime",a):
        print(l[49][6:])
        print(l[50][6:])  
    if query("fibonacci",a):
        print(l[51][6:])
        print(l[52][6:]) 
    if query("palindrome",a):
        print(l[53][6:])
    if query("factor",a) or query("factors",a) or query("multiple",a):
        print(l[54][6:])       
    if query("leap",a):
        print(l[55][6:])
        print(l[56][6:])
    if query("armstrong",a):
        print(l[57][6:])
        print(l[58][6:])
    if query("hcf",a) or query("gcd",a) or(query("highest",a) and query("common",a)):
        print(l[59][6:])
    if query("roots",a) or query("zeros",a) or query("quadratic",a) or query("cubic",a):
        print(l[60][6:])         
        print(l[61][6:])
