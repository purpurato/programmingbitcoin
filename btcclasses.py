import unittest 
#import TestCase

# Data for bitcoin elliptic curve secp256k1
# P is the prime number of the finite field
P = 2**256 - 2**32 - 977
# A, B are the coefficients of y**2 = x**3 + A*x + B
A = 0
B = 7
# N is the space dimension
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

class FieldElement:
    def __init__(self, num, prime):
        if num < 0 or num >= prime: 
            error = 'Num {} not in field range 0 to {}'.format(num, prime-1)
            raise ValueError(error)
        self.num = num 
        self.prime = prime

    def __eq__(self, other): 
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime
    def __repr__(self):
        return 'FieldElement_{}({})'.format(self.prime, self.num)
        
    def __add__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in different fields')
        num = (self.num + other.num) % self.prime
        return self.__class__(num, self.prime)
        
    def __sub__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot substract two numbers in different fields')
        num = (self.num - other.num) % self.prime
        return self.__class__(num, self.prime)
        
    def __mul__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot multiply 2 numbers in different fields')
        num = (self.num * other.num) % self.prime
        return self.__class__(num, self.prime)
        
    def __pow__(self, exponent):
        # Exponent is not a field element
        n = exponent % (self.prime - 1)
        num = pow(self.num, n, self.prime)
        return self.__class__(num, self.prime)
        
    def __truediv__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot divide 2 numbers in different fields')
        num = (self.num * other.num**(self.prime-2)) % self.prime        
        return self.__class__(num, self.prime)

class Point:
    """Defines point in an elliptic curve of the form 
    y**2 = x**3 + a*x + b. Parameters for bitcoin curve
    secp256k1 with a = 0 and b = 7 and p = 2**256-2**32-977"""
    zero = 0
    def __init__(self, x, y, a, b):
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        
        if self.x is None and self.y is None:
            return 
        
        if self.y**2 != self.x**3 + self.a*self.x + self.b:
            raise ValueError('Point ({}, {}, {}, {}) is not on the curve'.format(x,y,a,b))
    
    def __repr__(self):
        return 'Point({}, {})'.format(self.x, self.y)

    def __add__(self, other):
        if self.a != other.a or self.b != other.b:
            raise TypeError('Points {}, {} are not on the same curve'.format(self, other))
        
        if self.x is None:
            return other
        if other.x is None:
            return self
        
#        if self.y == -other.y:
#            return self.__class__(None, None, self.a, self.b)
        
        if self.x != other.x:
            s = (other.y - self.y) / (other.x - self.x)
            xres = s**2 - self.x - other.x
            yres = s*(self.x - xres) - self.y
            return Point(xres, yres, self.a, self.b)
        
        if self == other:
            s = (self.x**2 + self.x**2 + self.x**2 + self.a) / (self.y + self.y)
            xres = s**2 - (self.x + self.x)
            yres = s*(self.x - xres) - self.y
            return Point(xres, yres, self.a, self.b)
        
        if self == other and self.y == self.zero:
            return self.__class__(None, None, self.a, self.b)
    
    def __rmul__(self, coef):
        current = self
        result = self.__class__(None, None, self.a, self.b)
        while coef:
            if coef & 1:
                result += current
            current += current
            coef >>= 1
        return result
class S256Field(FieldElement):
    def __init__(self, num, prime=None):
        super().__init__(num=num, prime=P)
        
    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)
class S256Point(Point):
    zero = S256Field(0)
    def __init__(self, x, y, a=None, b=None):
        a, b = S256Field(A), S256Field(B)
        if type(x) == int:
            super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
        else:
            super().__init__(x=x, y=y, a=a, b=b)
            
    def __repr__(self):
        if self.x is None:
            return 'Point(infinity)'
        else:
            return 'Point({}, {})'.format(self.x, self.y)
            
    def __rmul__(self, coefficient):
        coef = coefficient % N
        return super().__rmul__(coef)
G = S256Point(  0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
                0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)

class ECCTest(unittest.TestCase):
    def test_on_curve(self):   
        prime = 223
        a = FieldElement(0, prime)
        b = FieldElement(7, prime)   
        valid_points = ((192, 105), (17, 56), (1, 193))
        invalid_points = ((200,119), (42,99))
        
        for x_raw, y_raw in valid_points:
            x = FieldElement(x_raw, prime)
            y = FieldElement(y_raw, prime)
            Point(x,y,a,b)
        
        for x_raw, y_raw in invalid_points:
            x = FieldElement(x_raw, prime)
            y = FieldElement(y_raw, prime)
            with self.assertRaises(ValueError):
                Point(x,y,a,b)            
        
        one = ((170,142),(60,139))
        #other tests can be done with pairs two = (47,71) + (17,56)
        sum = Point(None,None,a,b)
        for x, y in one:
            sum += Point(FieldElement(x,prime), FieldElement(y,prime),a,b)
        print(sum)


#if __name__ == '__main__':
#    unittest.main()

# This works ok 
prime = 0xdf
a = FieldElement(0, prime)
b = FieldElement(0x07, prime)
x = FieldElement(0x2f, prime)
y = FieldElement(0x47, prime)
p = Point(x, y, a, b)
for s in range(20,31):
    result = s*p
    print(result)

gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
x = FieldElement(gx, P)
y = FieldElement(gy, P)
seven = FieldElement(7, P)
zero = FieldElement(0, P)
G = Point(x, y, zero, seven)

# This doesn't work anymore
# print(5*G)
