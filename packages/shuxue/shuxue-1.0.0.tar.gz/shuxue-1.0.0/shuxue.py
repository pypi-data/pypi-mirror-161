#gaodengleixing
# 内部变量规范
# n m t: 特征量
# i j k : 变化的序号
# ai aij bi : 元素
# 全拼 : 变量
# 简拼 : 局部变量
# 首字母 : 原有类型

#hanshu
# nn 个数
# dd 精度
# qj 区间



import math


class juzhen(list):

    def __init__(self,l):
        list.__init__(self,[list(ai) for ai in l])
        self.n=len(l)
        self.m=len(l[0])

    def __call__(self,f):
        return juzhen([list(map(f,ai)) for ai in self])

    def copy(self):
        return juzhen([ai.copy() for ai in self])

    def __bool__(self):
        for ai in self:
            for aij in ai:
                if aij: return True
        return False

    def __eq__(self, other):
        if isinstance(other,juzhen):
            if self.n!=other.n:return False
            for i in range(self.n):
                if self[i]!=other[i] : return False
            return True
        elif isinstance(other,xiangliang):
            return self==other.juzhen()
        else:
            if self.n!=self.m:return False
            return self==juzhen.danweijuzhen(self.n,other)

    def __ne__(self, other):
        return not self.__eq__()

    def __lt__(self, other):
        for ai in self:
            for aij in ai:
                if abs(aij) >= other: return False
        return True

    def __gt__(self):
        return not self.__lt__()

    def __le__(self, other):
        for ai in self:
            for aij in ai:
                if abs(aij) > other: return False
        return True

    def __ge__(self):
        return not self.__le__()

    def __str__(self):
        return 'juzhen=([\n' + ',\n'.join([
            str(ai)
            for ai in self]) + ',\n])'

    def __repr__(self):
        return self.__str__()

    def __format__(self, format_spec):
        return 'juzhen=([\n[' + '],\n['.join(
            [','.join([aij.__format__(format_spec) for aij in ai]
            )for ai in self]) + '],\n])'

    def __pos__(self):
        return self

    def __neg__(self):
        return juzhen([[-aij for aij in ai] for ai in self])

    def __abs__(self):
        if 1==self.n==self.m :
            return self[0][0]
        else:
            he=False
            for i in range(self.n):
                he+=(-1)**i*self[i][0]*juzhen(
                [self[j][1:] for j in range(self.m) if j!=i]).__abs__()
            return he

    def hanglieshi(self):
        return self.__abs__()

    def __invert__(self):
        return juzhen([[~aij for aij in ai] for ai in self])

    def __len__(self,fx=False):
        if fx:
            return self.m
        else:
            return self.n

    def __round__(self, n=None):
        return juzhen([[aij.__round__(n) for aij in ai] for ai in self])

    def __floor__(self):
        return juzhen([[aij.__floor__() for aij in ai] for ai in self])

    def __ceil__(self):
        return juzhen([[aij.__ceil__ for aij in ai] for ai in self])

    def __trunc__(self):
        return juzhen([[aij.__trunc__() for aij in ai] for ai in self])

    def __add__(self, other):
        if isinstance(other,juzhen):
            return juzhen([[
                self[i][j]+other[i][j]
                for j in range(self.m)
                ]for i in range(self.n)])
        elif isinstance(other,xiangliang):
            return self+other.juzhen()
        else:
            return juzhen([[self[i][j]+other if i==j else self[i][j]
                for j in range(self.m)]
                for i in range(self.n)])

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other,juzhen):
            return juzhen([[
                self[i][j]-other[i][j]
                for j in range(self.m)
                ]for i in range(self.n)])
        elif isinstance(other,xiangliang):
            return self-other.juzhen()
        else:
            return juzhen([[self[i][j]-other if i==j else self[i][j]
                for j in range(self.m)]
                for i in range(self.n)])

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        if isinstance(other,juzhen):
            def diancheng(n,m,self=self,other=other):
                he=False
                for i in range(self.m):
                    he+=self[n][i]*other[i][m]
                return he
            return juzhen([[diancheng(i,j)
                for j in range(other.m)
                ]for i in range(self.n)])
        elif isinstance(other,xiangliang):
            return self*other.juzhen()
        else:
            return juzhen([[self[i][j]*other
                for j in range(self.m)]
                for i in range(self.n)])

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other,juzhen):
            return self*other.ni()
        return juzhen([[aij/other for aij in ai] for ai in self])

    def __floordiv__(self, other):
        return juzhen([[aij//other for aij in ai] for ai in self])

    def __mod__(self, other):
        return juzhen([[aij%other for aij in ai] for ai in self])

    def __divmod__(self, other):
        return juzhen([[divmod(aij,other) for aij in ai] for ai in self])

    def ni(self):
        hls=self.__abs__()
        return juzhen([[
            (-1)**(i+j)*juzhen(
            [ai[:j]+ai[j+1:] for ai in (self[:i]+self[i+1:])]
            ).__abs__()/hls
            for i in range(self.n)] for j in range(self.m)])

    def __rdiv__(self, other):
        return self.ni() * other

    def zhuanzhi(self):
        return juzhen([[self[i][j] for i in range(self.n)]
            for j in range(self.m)])

    def T(self):
        return self.zhuanzhi()

    def __pow__(self, power, modulo=None):
        if isinstance(power,zhengxushu):
            if power.imag != 0:
                return self**(T0*power.real)*(self**(T0*power.imag)).zhuanzhi()
            if power.real>0:
                fb=self.copy()
                for _ in range(int(power.real)-1):
                    fb*=self
                return fb
            elif power.real==0:
                return juzhen.danwei(self.n)
            else:
                return self.ni().__pow__(-power)
        else:
            return juzhen([[aij**power for aij in ai] for ai in self])

    def mi(self,n):
        return self**zhengxushu(n)

    def __lshift__(self, other):
        return juzhen([[aij<<other for aij in ai] for ai in self])

    def __rshift__(self, other):
        return juzhen([[aij>>other for aij in ai] for ai in self])

    def __and__(self, other):
        if isinstance(other,juzhen):
            return juzhen([[
                self[i][j]&other[i][j]
                for j in range(self.m)
                ]for i in range(self.n)])
        elif isinstance(other,xiangliang):
            return self&other.juzhen()
        else:
            return juzhen([[self[i][j]%other if i==j else self[i][j]
                for j in range(self.m)]
                for i in range(self.n)])

    def __rand__(self, other):
        return self & other

    def __xor__(self, other):
        if isinstance(other, juzhen):
            return juzhen([[
                self[i][j] ^ other[i][j]
                for j in range(self.m)
            ] for i in range(self.n)])
        elif isinstance(other, xiangliang):
            return self ^ other.juzhen()
        else:
            return juzhen([[self[i][j] ^ other if i == j else self[i][j]
                for j in range(self.m)]
                for i in range(self.n)])

    def __rxor__(self, other):
        return self ^ other

    def __or__(self, other):
        if isinstance(other, juzhen):
            return juzhen([[
                self[i][j] | other[i][j]
                for j in range(self.m)
            ] for i in range(self.n)])
        elif isinstance(other, xiangliang):
            return self | other.juzhen()
        else:
            return juzhen([[self[i][j] | other if i == j else self[i][j]
                for j in range(self.m)]
                for i in range(self.n)])

    def __ror__(self, other):
        return self | other

    def __iadd__(self, other):
        return self+other

    def __isub__(self, other):
        return self-other

    def __imul__(self, other):
        return self * other

    def __itruediv__(self, other):
        return self/other

    def __ifloordiv__(self, other):
        return self//other

    def __imod__(self, other):
        return self%other

    def __ipow__(self, other):
        return self**other

    def __ilshift__(self,other):
        return self<<other

    def __irshift__(self, other):
        return self>>other

    def __iand__(self, other):
        return self&other

    def __ixor__(self, other):
        return self^other

    def __ior__(self, other):
        return self|other

    def __complex__(self):
        if self.n == self.m:
            for i in self.n:
                if not self[i][i] == self[0][0]:
                    break
            else:
                return complex(self[0][0])

    def __int__(self):
        if self.n == self.m:
            for i in self.n:
                if not self[i][i] == self[0][0]:
                    break
            else:
                return int(self[0][0])

    def __float__(self):
        if self.n==self.m:
            for i in self.n:
                if not self[i][i]==self[0][0]:
                    break
            else:
                return float(self[0][0])


    def __contains__(self, item):
        for ai in self:
            if item in ai : return True
        else:
            return False

    def hang(self,n,l=None):
        if l==None:
            return hangxiangliang(self[n])
        else:
            self[n]=l
            return self

    def lie(self,n,l=None):
        if l==None:
            return liexiangliang([ai[n] for ai in self])
        else:
            for i in range(self.n): self[i][n]=l[i]
            return self

    def yuansubianhuan(self,f):
        return juzhen([[f(aij) for aij in ai] for ai in self])

    @classmethod
    def kong(cls,n,m,a=0):
        return cls([[a]*m for _ in range(n)])

    @classmethod
    def danwei(cls,n,a1=1,a0=0):
        dwjz=cls.kong(n,n,a0)
        for i in range(n):dwjz[i][i]=a1
        return dwjz

    @classmethod
    def pinjie(cls,jz1,jz2,fx):
        if fx :
            return cls([jz1[i]+jz2[i] for i in range(jz1.n)])
        else:
            return cls(list(jz1)+list(jz2))
    @classmethod
    def wenbenchuangjian(cls,s,lx=float):
        return  juzhen([[lx(aij) for aij in ai]
                        for ai in cls([si.split(' ') for si in
                        s.strip('\n').split('\n')])])



class zhengxushu(complex):
    def __str__(self):
        return ''.join(['T0*',str(self.real),'+T1*',str(self.imag)])
    def __format__(self, format_spec):
        return ''.join(['T0*',self.real.__format__(format_spec),
            '+T1*',self.imag.__format__(format_spec)])
    def __mul__(self, other):
        other=complex(other)
        return zhengxushu(
            (self.real*other.real+self.imag*other.imag
            )+(self.imag*other.real+self.real*other.imag)*1j)
    def ni(self):
        a2_b2=self.real**2-self.imag**2
        return zhengxushu(self.real/a2_b2-self.imag/a2_b2*1j)
    def __pow__(self, power, modulo=None):
        if power>0 :
            ji=zhengxushu(self)
            for i in range(power-1):
                ji*=self
            return ji
        elif power<0:
            return self.ni()**-power
        else:
            return zhengxushu(self)
    def __truediv__(self, other):
        return self*zhengxushu(other).ni()
    def __add__(self, other):
        return zhengxushu(complex.__add__(self,other))
    def __sub__(self, other):
        return zhengxushu(complex.__sub__(self,other))
T0=zhengxushu(1,0)
T1=zhengxushu(0,1)


class xiangliang(list):

    def __init__(self,fx,l):
        list.__init__(self,l)
        self.n=len(self)
        self.fangxiang=fx

    def __call__(self, f):
        return xiangliang(self.fangxiang,list(map(f,self)))

    def copy(self):
        return xiangliang(self.fangxiang,self)

    def __bool__(self):
        for ai in self:
            if ai : return True
        return False

    def juzhen(self):
        if self.fangxiang:
            return juzhen([self])
        else:
            return juzhen([[ai] for ai in self])

    def __eq__(self, other):
        if isinstance(other,xiangliang):
            return tuple(self)==tuple(other)
        elif isinstance(other,juzhen):
            return self.juzhen()==other
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        for ai in self:
            if abs(ai)>=other:return False
        return True

    def __gt__(self,other):
        return not self.__lt__(other)

    def __le__(self, other):
        for ai in self:
            if abs(ai) > other: return False
        return True

    def __ge__(self, other):
        return not self.__le__(other)

    def __str__(self):
        if self.fangxiang :
            return 'xiangliang(True,'+str(list(self))+')'
        else:
            return 'xiangliang(False,[\n'+',\n'.join(
                [str([ai])[1:-1] for ai in self]
                )+',\n])'

    def __repr__(self):
        return self.__str__()

    def __format__(self, format_spec):
        if self.fangxiang :
            return 'xiangliang(True,['+','.join(
                [ai.__format__(format_spec) for ai in self]
                )+'])'
        else:
            return 'xiangliang(False,[\n'+',\n'.join(
                [ai.__format__(format_spec) for ai in self]
                )+',\n])'

    def __pos__(self):
        return self

    def __neg__(self):
        return xiangliang(self.fangxiang,[-ai for ai in self])

    def __abs__(self):
        he=False
        for ai in self:
            he+=ai**2
        return he**0.5

    def mo(self):
        return self.__abs__()

    def __invert__(self):
        return xiangliang(self.fangxiang,[~ai for ai in self])

    def __round__(self, n=None):
        return xiangliang(self.fangxiang,[ai.__round__(n) for ai in self])

    def __floor__(self):
        return xiangliang(self.fangxiang,[ai.__floor__() for ai in self])

    def __ceil__(self):
        return xiangliang(self.fangxiang, [ai.__ceil__ for ai in self])

    def __trunc__(self):
        return xiangliang(self.fangxiang,[ai.__trunc__() for ai in self])

    def __add__(self, other):
        if isinstance(other,xiangliang):
            if self.fangxiang==other.fangxiang:
                return xiangliang(self.fangxiang,[self[i]+other[i] for i in range(self.n)])
        elif isinstance(other,juzhen):
            return self.juzhen()+other
        elif not other:
            return self

    def __radd__(self, other):
        return self+other

    def __sub__(self, other):
        if isinstance(other, xiangliang):
            if self.fangxiang == other.fangxiang:
                return xiangliang(self.fangxiang,[self[i] - other[i] for i in range(self.n)])
        elif isinstance(other, juzhen):
            return self.juzhen() - other

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        if isinstance(other,juzhen):
            return self.juzhen()*other
        elif isinstance(other,xiangliang):
            if other.fangxiang^self.fangxiang :
                other.fangxiang=not other.fangxiang
                return self.diancheng(other)
        else:
            return xiangliang(self.fangxiang,[ai*other for ai in self])

    def __rmul__(self, other):
        return self*other

    def __truediv__(self, other):
        return xiangliang(self.fangxiang,[ai/other for ai in self])

    def __floordiv__(self, other):
        return xiangliang(self.fangxiang,[ai//other for ai in self])

    def __mod__(self, other):
        return xiangliang(self.fangxiang,[ai%other for ai in self])

    def __divmod__(self, other):
        return xiangliang(self.fangxiang,[divmod(self,other) for ai in self])

    def __pow__(self, power, modulo=None):
        if isinstance(power,zhengxushu):
            if power.imag==1:
                return self.zhuanzhi()
            if not power.imag :
                return self**power.real
        return xiangliang(self.fangxiang, [ai ** power for ai in self])

    def zhuanzhi(self):
        return xiangliang(not self.fangxiang,self)

    def T(self):
        return self.zhuanzhi()

    def __lshift__(self, other):
        return xiangliang(self.fangxiang,[ai>>other for ai in self])

    def __rshift__(self, other):
        return xiangliang(self.fangxiang,[ai<<other for ai in self])

    def __and__(self, other):
        if isinstance(other,xiangliang):
            if self.fangxiang==other.fangxiang:
                return xiangliang([self[i]&other[i] for i in range(self.n)])
        elif isinstance(other,juzhen):
            return self.juzhen()&other

    def __rand__(self, other):
        return self & other

    def __xor__(self, other):
        if isinstance(other,xiangliang):
            if self.fangxiang==other.fangxiang:
                return xiangliang([self[i]^other[i] for i in range(self.n)])
        elif isinstance(other,juzhen):
            return self.juzhen()^other

    def __rxor__(self, other):
        return self ^ other

    def __or__(self, other):
        if isinstance(other,xiangliang):
            if self.fangxiang==other.fangxiang:
                return xiangliang([self[i]|other[i] for i in range(self.n)])
        elif isinstance(other,juzhen):
            return self.juzhen()|other

    def __ror__(self, other):
        return self | other

    def __iadd__(self, other):
        return self+other

    def __isub__(self, other):
        return self-other

    def __imul__(self, other):
        return self * other

    def __itruediv__(self, other):
        return self/other

    def __ifloordiv__(self, other):
        return self//other

    def __imod__(self, other):
        return self%other

    def __ipow__(self, other):
        return self**other

    def __ilshift__(self,other):
        return self<<other

    def __irshift__(self, other):
        return self>>other

    def __iand__(self, other):
        return self&other

    def __ixor__(self, other):
        return self^other

    def __ior__(self, other):
        return self|other

    def diancheng(self,xl):
        if self.fangxiang == xl.fangxiang and self.n == xl.n:
            he = 0
            for i in range(self.n):
                he += self[i] * xl[i]
            return he

    def chacheng(self,*xl):
        if len(xl)+2==self.n:
            jz=juzhen(
            [[xiangliang.danwei(self.fangxiang,self.n,i
            ) for i in range(self.n)]]+[self]+list(xl))
            return abs(jz)

    def yuansubianhuan(self,f):
        return xiangliang(self.fangxiang ,[f(ai) for ai in self])

    @classmethod
    def danwei(cls,fx,n,m,a1=1,a0=0):
        dwxl=[a0]*n
        dwxl[m]=a1
        return cls(fx,dwxl)

    @classmethod
    def wenbenchuanjian(cls,s='',lx=float):
        if s[0]=='\n':
            return cls(False,[lx(ai) for ai in s.strip('\n').split('\n')])
        else:
            return cls(True,[lx(ai) for ai in s.split(' ')] )


class hangxiangliang(xiangliang):
    def __init__(self,l):
        xiangliang.__init__(self,True,l)

class liexiangliang(xiangliang):
    def __init__(self,l):
        xiangliang.__init__(self,False,l)







class luoji:
    def __init__(self, b):
        self._b = b

    def __call__(self, *args, **kwargs):
        return self._b

    def __bool__(self):
        return self._b

    @classmethod
    def true(cls):
        return cls(True)

    @classmethod
    def false(cls):
        return cls(False)


true = luoji.true()
false = luoji.false()


class hanshu:
    x0 = 0
    x1 = 2 * math.pi
    dd = 10 ** -6
    nn = 2 ** 16
    tj = true

    def __init__(self, f):
        if isinstance(f, hanshu):
            self.f = f.f
        else:
            self.f = f

    def __call__(self, *args, **kwargs):
        if self.tj(*args, **kwargs):
            return self.f(*args, **kwargs)
        else:
            print('超出定义域')

    def __copy__(self):
        g = hanshu(self.f)
        g.x0 = self.x0
        g.x1 = self.x1
        g.dd = self.dd
        g.nn = self.nn
        return g

    def gudingcanshu(self, *args, **kwargs):
        cs1 = args
        cs2 = kwargs

        def f(*args, **kwargs):
            args = cs1 + args[len(cs1):]
            kwargs |= cs2
            return self.f(*args, **kwargs)

        hs = self.__copy__()
        hs.f = f
        return hs

    def yiyuanhanshu(self, mc, *args, **kwargs):
        def f(x, mc=mc):
            xx = {mc: x}
            hs = self.gudingcanshu(*args, **kwargs)
            return hs(**xx)

        hs = self.__copy__()
        hs.f = f
        return hs

    def __pos__(self):
        return self.__copy__()

    def __neg__(self):
        hs = self.__copy__()

        def f(*args, **kwargs):
            return -self.f(*args, **kwargs)

        hs.f = f
        return hs

    def __abs__(self):
        hs = self.__copy__()

        def f(*args, **kwargs):
            return abs(self.f(*args, **kwargs))

        hs.f = f
        return hs

    def __invert__(self):
        hs = self.__copy__()

        def f(*args, **kwargs):
            return ~self.f(*args, **kwargs)

        hs.f = f
        return hs

    def __floor__(self):
        hs = self.__copy__()

        def f(*args, **kwargs):
            return self.f(*args, **kwargs).__floor__()

        hs.f = f
        return hs

    def __ceil__(self):
        def f(*args, **kwargs):
            return self.f(*args, **kwargs).__ceil__()

        hs = self.__copy__()
        hs.f = f
        return hs

    def __trunc__(self):
        def f(*args, **kwargs):
            return self.f(*args, **kwargs).__trunc__()

        hs = self.__copy__()
        hs.f = f
        return hs

    def __add__(self, other):
        if isinstance(other, hanshu):
            def f(*args, **kwargs):
                return self(*args, **kwargs) + other(*args, **kwargs)

            hs = self.__copy__()
            hs.f = f
            return hs
        else:
            def f(*args, **kwargs):
                return self(*args, **kwargs) + other

            hs = self.__copy__()
            hs.f = f
            return hs

    def __sub__(self, other):
        if isinstance(other, hanshu):
            def f(*args, **kwargs):
                return self(*args, **kwargs) - other(*args, **kwargs)

            hs = self.__copy__()
            hs.f = f
            return hs
        else:
            def f(*args, **kwargs):
                return self(*args, **kwargs) - other

            hs = self.__copy__()
            hs.f = f
            return hs

    def __mul__(self, other):
        if isinstance(other, hanshu):
            def f(*args, **kwargs):
                return self(*args, **kwargs) * other(*args, **kwargs)

            hs = self.__copy__()
            hs.f = f
            return hs
        else:
            def f(*args, **kwargs):
                return self(*args, **kwargs) * other

            hs = self.__copy__()
            hs.f = f
            return hs

    def __floordiv__(self, other):
        if isinstance(other, hanshu):
            def f(*args, **kwargs):
                return self(*args, **kwargs) // other(*args, **kwargs)

            hs = self.__copy__()
            hs.f = f
            return hs
        else:
            def f(*args, **kwargs):
                return self(*args, **kwargs) // other

            hs = self.__copy__()
            hs.f = f
            return hs

    def __truediv__(self, other):
        if isinstance(other, hanshu):
            def f(*args, **kwargs):
                return self(*args, **kwargs) / other(*args, **kwargs)

            hs = self.__copy__()
            hs.f = f
            return hs
        else:
            def f(*args, **kwargs):
                return self(*args, **kwargs) / other

            hs = self.__copy__()
            hs.f = f
            return hs

    def __mod__(self, other):
        if isinstance(other, hanshu):
            def f(*args, **kwargs):
                return self(*args, **kwargs) % other(*args, **kwargs)

            hs = self.__copy__()
            hs.f = f
            return hs
        else:
            def f(*args, **kwargs):
                return self(*args, **kwargs) % other

            hs = self.__copy__()
            hs.f = f
            return hs

    def __pow__(self, power, modulo=None):
        if isinstance(power, hanshu):
            def f(*args, **kwargs):
                return self(*args, **kwargs) ** power(*args, **kwargs)

            hs = self.__copy__()
            hs.f = f
            return hs
        else:
            def f(*args, **kwargs):
                return self(*args, **kwargs) ** power

            hs = self.__copy__()
            hs.f = f
            return hs

    def __irshift__(self, other):
        if isinstance(other, hanshu):
            def f(*args, **kwargs):
                return self(*args, **kwargs) << other(*args, **kwargs)

            hs = self.__copy__()
            hs.f = f
            return hs
        else:
            def f(*args, **kwargs):
                return self(*args, **kwargs) << other

            hs = self.__copy__()
            hs.f = f
            return hs

    def __rshift__(self, other):
        if isinstance(other, hanshu):
            def f(*args, **kwargs):
                return self(*args, **kwargs) >> other(*args, **kwargs)

            hs = self.__copy__()
            hs.f = f
            return hs
        else:
            def f(*args, **kwargs):
                return self(*args, **kwargs) >> other

            hs = self.__copy__()
            hs.f = f
            return hs

    def __and__(self, other):
        if isinstance(other, hanshu):
            def f(*args, **kwargs):
                return self(*args, **kwargs) & other(*args, **kwargs)

            hs = self.__copy__()
            hs.f = f
            return hs
        else:
            def f(*args, **kwargs):
                return self(*args, **kwargs) & other

            hs = self.__copy__()
            hs.f = f
            return hs

    def __or__(self, other):
        if isinstance(other, hanshu):
            def f(*args, **kwargs):
                return self(*args, **kwargs) | other(*args, **kwargs)

            hs = self.__copy__()
            hs.f = f
            return hs
        else:
            def f(*args, **kwargs):
                return self(*args, **kwargs) | other

            hs = self.__copy__()
            hs.f = f
            return hs

    def __xor__(self, other):
        if isinstance(other, hanshu):
            def f(*args, **kwargs):
                return self(*args, **kwargs) ^ other(*args, **kwargs)

            hs = self.__copy__()
            hs.f = f
            return hs
        else:
            def f(*args, **kwargs):
                return self(*args, **kwargs) ^ other

            hs = self.__copy__()
            hs.f = f
            return hs

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return self - other

    def __rmul__(self, other):
        return self * other

    def __rand__(self, other):
        return self & other

    def __ror__(self, other):
        return self | other

    def __rxor__(self, other):
        return self ^ other

    def __iand__(self, other):
        return self + other

    def __isub__(self, other):
        return self - other

    def __imul__(self, other):
        return self * other

    def __ifloordiv__(self, other):
        return self // other

    def __idiv__(self, other):
        return self / other

    def __itruediv__(self, other):
        return self / other

    def __imod__(self, other):
        return self % other

    def __ipow__(self, other):
        return self ** other

    def __ilshift__(self, other):
        return self << other

    def __irshift__(self, other):
        return self >> other

    def __iand__(self, other):
        return self & other

    def __ior__(self, other):
        return self | other

    def __ixor__(self, other):
        return self ^ other

    def youdaoshu(self, dd=dd):
        dd = dd * 10 ** -8

        def d(x):
            return (self(x + 2 * dd) - self(x + dd)) / dd

        hs = self.__copy__()
        hs.f = d
        return hs

    def zuodaoshu(self, dd=dd):
        dd = dd * 10 ** -8
        hs = self.__copy__()

        def d(x):
            return (self(x + 2 * dd) - self(x + dd)) / dd

        hs.f = d
        return hs

    def daoshu(self, dd=None):
        hs = self.__copy__()
        if dd == None:
            def d(x, dd=self.dd * 10 ** 5):
                n0 = self(x)
                fx1 = self(x - 1.5 * dd)
                fx2 = self(x - 0.5 * dd)
                fx3 = self(x + 0.5 * dd)
                fx4 = self(x + 1.5 * dd)
                n3 = (3 * fx2 - 3 * fx3 + fx4 - fx1) / (dd ** 3)
                if n3:
                    dd = abs((n0 * 10 ** -16) / n3) ** (1 / 3) / 2
                else:
                    dd = self.dd
                return ((self(x + dd) - self(x - dd)) / dd / 2)
        else:
            def d(x, dd=self.dd):
                return (self(x + 0.5 * dd) - self(x - 0.5 * dd)) / dd
        hs.f = d
        return hs

    def zuojixian(self, x0, dd=dd):

        return self(x0 - dd) + self.zuodaoshu(dd)(x0 - dd) * dd

    def youjixian(self, x0=x0, dd=dd):

        return self(x0 + dd) - self.youdaoshu(dd)(x0 + dd) * dd

    def jixian(self, x0=x0, dd=dd):

        return (self.youjixian(x0, dd) + self.zuojixian(x0, dd)) / 2

    def dingjifen(self, x0=x0, x1=x1, nn=nn):
        d = (x1 - x0) / nn
        he = (self(x0 + 0.25 * d) + self(x1 - 0.25 * d)) / 2
        for i in range(nn - 1):
            he += self(x0 + (i + 1) * d)
        return he / nn * (x1 - x0)

    def budingjifen(self, x0=x0, nn=nn):
        hs = self.__copy__()

        def j(x):
            return self.dingjifen(x0, x, nn)

        hs.f = j
        return hs

    def jiefangcheng(self, x0=x0, dd=None):
        jie = (x0, self(x0))
        if dd == None:
            dd = max([abs(self.daoshu(self.dd)(x0) * 10 ** -16), self(x0) * 10 ** -16])
        for i in range(self.nn):
            fx = self(x0)
            Dfx = self.daoshu(dd)(x0)
            if abs(fx) < dd:
                return (x0, self(x0))
            else:
                if abs(Dfx) <= dd:
                    return jie
                else:
                    if abs(fx) < abs(jie[1]):
                        jie = (x0, self(x0))
                    x0 -= fx / Dfx
        return jie

    def zuixiaozhi(self, x0=x0, x1=x1, nn=nn):

        d = (x1 - x0) / nn
        fx0 = self.youjixian(x0)
        fx1 = self.zuojixian(x1)
        if fx1 < fx0:
            zuixiao = (x0, fx0)
        else:
            zuixiao = (x1, fx1)
        for i in range(nn - 1):
            x = x0 + (i + 1) ** d
            if self(x) < zuixiao[1]:
                zuixiao = (x, self(x))
        if zuixiao[1] == fx1 or zuixiao[1] == fx1:
            return zuixiao
        else:
            jie = self.daoshu().jiefangcheng()
            return (jie[0], self(jie[0]))

    def zuidazhi(self, x0=x0, x1=x1, nn=nn):
        zxz = -self.zuixiaozhi(x0, x1, nn)
        return (zxz[0], -zxz[1])

    def zuizhi(self, x0=x0, x1=x1, nn=nn):
        return (self.zuixiaozhi(x0, x1, nn), self.zuidazhi(x0, x1, nn))

    def youpiandao(self, mc, *args, **kwargs):
        def f(x, mc=mc):
            xx = {mc: x}
            hs = self.gudingcanshu(*args, **kwargs)
            return hs(**xx)

        hs = self.__copy__()
        hs.f = f
        return hs.youdaoshu

    def zuopiandao(self, mc, *args, **kwargs):
        def f(x, mc=mc):
            xx = {mc: x}
            hs = self.gudingcanshu(*args, **kwargs)
            return hs(**xx)

        hs = self.__copy__()
        hs.f = f
        return hs.zuodaoshu

    def piandao(self, mc, *args, **kwargs):

        def f(x, mc=mc):
            xx = {mc: x}
            hs = self.gudingcanshu(*args, **kwargs)
            return hs(**xx)

        hs = self.__copy__()
        hs.f = f
        return hs.daoshu

    def chongjifen(self, *qj, nn=nn):
        nn = int(nn ** (1 / len(qj)) * len(qj))
        he = 0
        for i in bianliqujian(nn, *qj):
            he += self(*i)
        else:
            return he / (nn ** len(qj)) * leiji([abs(ai[1] - ai[0]) for ai in qj])

    def zuixiaozhis(self, *qj, nn=nn):
        n = len(qj)
        nn = int(nn ** (1 / n) * n)
        zxz = None
        for i in bianliqujian(nn, *qj):
            if zxz == None:
                zxz = i
            else:
                cxz = i
                break

        for i in bianliqujian(nn, *qj):
            if self(*i) < self(*zxz):
                zxz = i
            elif self(*i) < self(*cxz):
                cxz = i

        zxz = hangxiangliang(zxz)
        cxz = hangxiangliang(cxz)

        @hanshu
        def f(k, zxz=zxz, cxz=cxz):
            return self(*(zxz + k * (cxz + zxz)))

        jg = f.zuixiaozhi(nn, -0.5, 1)
        return [list(zxz + jg[0] * (cxz + zxz)), jg[1]]

    def zuidazhis(self, *qj, nn=nn):
        zxz = (-self).zuixiaozhis(nn, *qj)
        return [zxz[0], -zxz[1]]

    def zuizhis(self, *qj, nn=nn):
        return [self.zuixiaozhis(nn, *qj), self.zuidazhis(nn, *qj)]

    def jiefangchengs(self, *qj, nn=nn):
        return abs(self).zuixiaozhis(nn, *qj)


def jiecheng(n):
    ji = True
    for i in range(n):
        ji *= i + 1
    return ji


def leihe(l):
    try:
        return sum(l)
    except:
        try:
            return math.fsum(l)
        except:
            try:
                he = l[0]
                for ai in l[1:]:
                    he += ai
                return he
            except:
                he = None
                for ai in l:
                    if he == None:
                        he = ai
                    else:
                        he += ai


def leiji(l):
    ji = l[0]
    for ai in l[1:]:
        ji *= ai
    return ji


def bianliqujian(nn, *qj):
    n = len(qj)
    for i in range(nn ** n):
        l = [0] * n
        for j in range(n):
            l[j] = i % nn
            i //= nn
        else:
            yield [(qj[j][0] + (l[j] + 0.5) * (qj[j][1] - qj[j][0]) / nn) for j in range(n)]
















