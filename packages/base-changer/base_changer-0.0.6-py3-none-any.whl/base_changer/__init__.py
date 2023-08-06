name="base_changer"
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

def help():
    print()
    print("********************************************************************")   
    print()
    print("This module is developed by HARSH GUPTA.")
    print("This module can be used to convert one Number System to another.\n")
    print("TO SEARCH ALL AVAILABLE FUNCTIONS ...TYPE::")
    print("  >>>base_changer.index()\n")
    print("For example :")
    print("->TO CONVERT OCTAL TO DECIMAL ...type::")
    print("  >>>base_changer.converter.oct_to_dec(734)")    
    print()
    print("********************************************************************")


L=[
  f'',  
  f'1.CONVERT BINARY TO DECIMAL \n Syntax -> {name}.converter.bin_to_dec(<binary_number>)',   
  f'2.CONVERT BINARY TO OCTAL \n Syntax -> {name}.converter.bin_to_oct(<binary_number>)',   
  f'3.CONVERT BINARY TO HEXADECIMAL \n Syntax -> {name}.converter.bin_to_hex(<binary_number>)',   
  f'4.CONVERT DECIMAL TO BINARY \n Syntax -> {name}.converter.dec_to_bin(<decimal_number>)',   
  f'5.CONVERT DECIMAL TO OCTAL \n Syntax -> {name}.converter.dec_to_oct(<decimal_number>)',  
  f'6.CONVERT DECIMAL TO HEXADECIMAL \n Syntax -> {name}.converter.dec_to_hex(<decimal_number>)',  
  f'7.CONVERT OCTAL TO BINARY \n Syntax -> {name}.converter.oct_to_bin(<octal_number>)',   
  f'8.CONVERT OCTAL TO DECIMAL \n Syntax -> {name}.converter.oct_to_dec(<octal_number>)',  
  f'8.CONVERT OCTAL TO HEXADECIMAL \n Syntax -> {name}.converter.oct_to_hex(<octal_number>)',  
  f'10.CONVERT HEXADECIMAL TO BINARY \n Syntax -> {name}.converter.hex_to_bin("<hexadecimal_number>")',   
  f'11.CONVERT HEXADECIMAL TO DECIMAL \n Syntax -> {name}.converter.hex_to_dec("<hexadecimal_number>")',   
  f'12.CONVERT HEXADECIMAL TO OCTAL \n Syntax -> {name}.converter.hex_to_oct("<hexadecimal_number>")'
  ]

def index():
    for i in L:
        print(i)


