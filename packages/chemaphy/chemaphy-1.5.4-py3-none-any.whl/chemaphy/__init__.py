import numpy as np
import pandas as pd
import math
import trigo
import statistics as stats


            #NOTE#
"""
    Constants
"""

class Constant:
    def __init__(self,value,units,info):
        self.value = value
        self.units = units
        self.info = info


h = Constant(6.626e-34,"joule sec","Plancl's Constant")
e = Constant(1.6e-19,"C","Charge on electron")
epsilon_0 = Constant(8.85e-12,"m^(-3) kg^(-1) s^4 A^2","permitivity in free space")
k = Constant(9e9,"N m^2 C^(-2)","Coulombs constant")
c = Constant(3e8,"m/s","speed of light in vacuum")
R = Constant(1.0973e7,"m^(-1)","Rydbergs's Constant")
gas_constant = Constant(8.3145,"J mol^(-1) K^(-1)","Gas Constant")

pi = Constant(3.1415,None,None)
exp = Constant(2.7182,None,None)
inf = Constant(np.inf,None,"Infinity")

ang = Constant(1e-10,"m","Angstrom Measuring unit `1A = 10^(-10)m`")
exa = Constant(1e18,None,None)
peta = Constant(1e15,None,None)
tera = Constant(1e12,None,None)
giga = Constant(1e9,None,None)
mega = Constant(1e6,None,None)
kilo = Constant(1e3,None,None)
hecto = Constant(1e2,None,None)
deca = Constant(1e1,None,None)
one = Constant(1e0,None,None)
zero = Constant(0e0,None,None)
deci = Constant(1e-1,None,None)
centi = Constant(1e-2,None,None)
milli = Constant(1e-3,None,None)
micro = Constant(1e-6,None,None)
nano = Constant(1e-9,None,None)
pico = Constant(1e-12,None,None)
femto = Constant(1e-15,None,None)
atto = Constant(1e-18,None,None)

mass_e = Constant(9.1e-31,"kg","Mass of electron")
e_amu = Constant(0.00054858,"amu","Mass of electron")
mass_p = Constant(1.67262e-27,"kg","Mass of proton")
p_amu = Constant(1.007825,"amu","Mass of proton")
mass_n = Constant(1.67493e-27,"kg","Mass of neutron")
n_amu = Constant(1.008665,"amu","Mass of neutron")

g_sun = Constant(274,"m/s^2","garvity on Sun")
g_mercury = Constant(3.7,"m/s^2","gravity on Mercury")
g_venus = Constant(8.87,"m/s^2","gravity on Venus")
g_earth = Constant(9.8,"m/s^2","gravity on Earth")
g_moon = Constant(1.62,"m/s^2","gravity on Moon")
g_mars = Constant(3.712,"m/s^2","gravity on Mars")
g_jupiter = Constant(24.79,"m/s^2","gravity on Jupiter")
g_saturn = Constant(10.44,"m/s^2","gravity on Saturn")
g_uranus = Constant(8.87,"m/s^2","gravity on Uranus")
g_neptune = Constant(11.15,"m/s^2","gravity on Neptune")
G = Constant(6.6743e-11,"m^3 kg^(-1) s^(-2)","Gravitational Constant")

mass_sun = Constant(1.989e30,"kg","Mass of Sun")
radius_sun = Constant(696340000,"m","Radius of Sun")
mass_mercury = Constant(6.39e23,"kg","Radius of Mercury")
radius_mercury = Constant(3389500,"m","Radius of Mercury")
mass_venus = Constant(4.867e24,"kg","Mass of Venus")
radius_venus = Constant(6051800,"m","Radius of Venus")
mass_earth = Constant(5.972e24,"kg","Mass of Earth")
radius_earth = Constant(6371800,"m","Radius of Earth")
mass_moon = Constant(7.347e22,"kg","Mass of Moon")
radius_moon = Constant(1737400,"m","Radius of Moon")
mass_mars = Constant(6.39e23,"kg","Mass of Mars")
radius_mars = Constant(3389500,"m","Radius of Mars")
mass_jupiter = Constant(1.898e27,"kg","Mass of Jupiter")
radius_jupiter = Constant(69911000,"m","Radius of Jupiter")
mass_saturn = Constant(5.683e26,"kg","Mass of Saturn")
radius_saturn = Constant(58232000,"m","Radius of Saturn")
mass_uranus = Constant(8.681e25,"kg","Mass of Sturn")
radius_uranus = Constant(25362000,"m","Radius of Uranus")
mass_neptune = Constant(1.024e26,"kg","Mass of Neptune")
radius_neptune = Constant(24622000,"m","Radius of Neptune")


data = pd.read_csv("https://raw.githubusercontent.com/Sahil-Rajwar-2004/Datasets/main/elements.csv")

class ModernPhysics:
    def kinetic_energy_of_electron(Z,n) -> int:
        K = (mass_e.value*(Z**2)*(e.value**4))/(8*(epsilon_0.value**2)*(h.value**2)*(n**2))
        return f"{round(K,70)} j"

    def potential_energy_of_atom(Z,n) -> int:
        V = -(mass_e.value*Z**2*e.value**4)/(4*epsilon_0.value**2*h.value**2*n**2)
        return f"{round(V,70)} j"

    def total_energy_of_atom(Z,n) -> int:
        E = -(mass_e.value*Z**2*e.value**4)/(8*epsilon_0.value**2*h.value**2*n**2)
        return f"{round(E,70)} j"

    def freq(wave_len) -> int:
        f = c.value/wave_len
        return f"{f} Hz"

    def energy_of_photon(wave_len) -> int:
        E = h.value*c.value/wave_len
        return f"{E} j"

    def momentum_of_electron(Z,n) -> int:
        vel = (2.18*10**(6)*Z)/n
        return f"{vel} kgm/s^2"

    def de_Broglie_wavelength_particle(mass,vel) -> int:
        wave_len = h.value/(mass*vel)
        return wave_len

    def half_life(decay_const) -> int:
        t = 0.693/decay_const
        return f"{round(t,2)} yrs"

    def binding_energy(element):
        elements = list(data["Element"].str.lower())
        protons = list(data["NumberofProtons"])
        neutrons = list(data["NumberofNeutrons"])
        atm_mass = list(data["AtomicMass"])

        pos = elements.index(element)
        return (protons[pos]*p_amu.value+neutrons[pos]*n_amu.value-atm_mass[pos])*931.5

    def binding_energy_nucleon(element:str):
        elements = list(data["Element"].str.lower())
        protons = list(data["NumberofProtons"])
        neutrons = list(data["NumberofNeutrons"])
        atm_mass = list(data["AtomicMass"])

        pos = elements.index(element)
        return ((protons[pos]*p_amu.value+neutrons[pos]*n_amu.value-atm_mass[pos])*931.5)/(protons[pos]+neutrons[pos])


class ClassicalPhysics:
    """
    mass: int
    acc: int
    """

    def Force(mass,acc) -> int:
        F = mass*acc
        return f"{F} N"

    """
    mass: int
    d(distance): int
    """

    def GravitationalField(mass_obj1,mass_obj2,d) -> int:
        F = (G.value*mass_obj1*mass_obj2)/d**2
        return f"{round(F,2)} N"

    def GravitationalPotential(mass_obj1,mass_obj2,d) -> int:
        U = -(G.value*mass_obj1*mass_obj2)/d
        return f"{round(U,2)} J/kg"

    """
    gravity: int
    r(radius): int
    """

    def EscapeVelocity(gravity,r) -> int:
        """
            The minimum velocity in which a body must have in order to escape
            the gravitational pull of a particular planet or other object.

            mass_e => mass of the body escape from
            r => distace from the center of mass 
        """
        Ve = math.sqrt(2*gravity*r)
        Ve = Ve/1000
        return f"{round(Ve,2)} km/s"

    """
    mass: int
    """

    def SchwarzschildRadius(m_obj) -> int:
        r = (2*G.value*m_obj)/c.value
        return f"{round(r,3)}"

    """
    r(radius): int
    f(force): int
    angle(deg): int
    """

    def Torque(r,f,angle) -> int:
        deg = np.deg2rad(angle)
        tau = r*f*trigo.sin(deg)
        return f"{round(tau,3)} Nm"

    """
    I(current): int
    R(Resistor): int
    """

    def Ohm(I,R) -> int:
        return f"{I*R} Volt"

    """
    F(force): int
    d(distance): int
    angle(int): int
    """

    def WorkDone(F,d,angle) -> int:
        deg = np.deg2rad(angle)
        W = F*d*trigo.sin(deg)
        return f"{round(W,3)} j"

    """
    W(watt): int
    t(time): int
    """

    def Power(W,t) -> int:
        return f"{W/t} Watt"

    def AvgSpeed(total_distance,total_time) -> int:
        avg = total_distance/total_time
        return f"{round(avg,2)} dist/time"

    def AvgVelocity(total_displacment,total_time) -> int:
        avg = total_displacment/total_time
        return f"{round(avg,2)} dist/time"


class ProjectileMotion:
    def HorizontalRange(velocity,gravity,angle) -> int:
        deg = np.deg2rad(angle)
        R = (velocity**2*trigo.sin(2*deg))/gravity
        return f"{round(R,2)} m"

    def MaximumHeight(velocity,gravity,angle) -> int:
        deg = np.deg2rad(angle)
        H = (velocity**2*(trigo.sin(deg)**2))/(2*gravity)
        return f"{round(H,2)} m"

    def TimeInterval(velocity,gravity,angle) -> int:
        deg = np.deg2rad(angle)
        T = (2*velocity*trigo.sin(deg))/gravity
        return f"{round(T,2)} sec"


class AlternatingCurrent:
    def Irms2I(rms) -> int:
        i = rms*math.sqrt(2)
        return f"{round(i,2)} Ampere"
    
    def I2Irms(current) -> int:
        rms = current/math.sqrt(2)
        return f"{round(rms,2)} Ampere"

    def Vrms2V(rms) -> int:
        v = rms*math.sqrt(2)
        return f"{round(v,2)} Volts"

    def V2Vrms(volt) -> int:
        rms = volt/math.sqrt(2)
        return f"{round(rms,2)} Volts"

    def AngularFrequency(frequency) -> int:
        w = 2*pi.value*frequency
        return w

    def CapacitanceReactance(freq,C) -> int:
        Xc = 1/(2*pi.value*freq*C)
        return f"{round(Xc,2)} Ohm"

    def InductiveReactance(freq,L) -> int:
        Xl = 2*pi.value*freq*L
        return f"{round(Xl,2)} Ohm"

    def Impedance(Xc,Xl,R) -> int:
        Z = math.sqrt(R**2+(Xl-Xc)**2)
        return f"{round(Z,2)} Ohm"

    def Phase(Xc,Xl,R) -> int:
        phi = trigo.arc_tan((Xc-Xl)/R)
        return f"{round(phi,2)}"

    def PowerDissipated(v,i) -> int:
        p = i**2*v
        return f"{round(p,2)}"

    def ResonanceFrequency(L,C) -> int:
        f = 1/(2*pi.value*math.sqrt(L*C))
        return f"{round(f,2)} Hz"

    def ParallelResonanceFrequency(L,C,R) -> int:
        f = (1/(2*pi.value))*math.sqrt(1/(L*C)-(R**2/L**2))
        return f"{round(f,2)} Hz"

    def QualitativeFactor(R,L,C) -> int:
        Q = (1/R)*math.sqrt(L/C)
        return f"{round(Q,2)}"


class Statistics:
    def Subtract(args:list,kwargs:list):
        if len(args) == len(kwargs):
            res = []
            for i in range(0,len(args)):
                x = args[i]-kwargs[i]
                res.append(x)
            return res
        else:
            return "length of args and kwargs are not equal"

    def Add(args:list,kwargs:list):
        if len(args) == len(kwargs):
            res = []
            for i in range(0,len(args)):
                x = args[i]+kwargs[i]
                res.append(x)
            return res
        else:
            return "length of args and kwargs are not equal"

    def Multiply(args:list,kwargs:list):
        if len(args) == len(kwargs):
            res = []
            for i in range(0,len(args)):
                x = args[i]*kwargs[i]
                res.append(x)
            return res
        else:
            return "length of args and kwargs are not equal"

    def Divide(args:list,kwargs:list):
        if len(args) == len(kwargs):
            res = []
            for i in range(0,len(args)):
                x = args[i]/kwargs[i]
                res.append(x)
            return res
        else:
            return "length of args and kwargs are not equal"

    def MinMax(args) -> list:
        sorting = sorted(args, reverse = False)
        return [sorting[0],sorting[len(sorting)-1]]

    def Count(args) -> list:
        return len(args)

    def Factorial(num) -> int:
        """
        It is the product of less than equal to n(number).\n
        Denoted as `n!`

        for more info: <https://www.google.com/search?q=factorial>

        ===========================\n
        Mathematical Representation\n
        ===========================\n
        `n! = n*(n-1)*(n-2)*...*1`
        """
        return math.factorial(num)

    def Permutations(n,r) -> int:
        """
        A technique to determines the number of possible arrangements in a set when the order of the arrangements matters.\n
        Denoted as `nPr` where `n` is total number of objects and `r` is selected objects for arrangements\n

        for more info: <https://www.google.com/search?q=permuation>

        ===========================\n
        Mathematical Representation\n
        ===========================\n
        `nPr = n!/(n-r)!`
        """
        return math.factorial(n)/math.factorial(n-r)

    def Combinations(n,r) -> int:
        """
        An arrangement of objects where the order in which the objects are selected doesn't matter.\n
        Denoted as 'nCr' where `n` is total number of objects in the set and `r` number of choosing objects from the set\n

        for more info: <https://www.google.com/search?q=combination>\n

        ===========================\n
        Mathematical Representation\n
        ===========================\n
        `nCr = n!/r!(n-r)!`
        """
        return math.factorial(n)/(math.factorial(r)*math.factorial(n-r))

    def Quartiles(args) -> list:
        """
        In statistics, a quartile is a type of quantile which divides the number of data points into four parts, or quarters, of more-or-less equal size\n
        the data must be in ascending order.\n

        for more info: <https://www.google.com/search?q=quartiles>\n
        """
        rel = sorted(args,reverse = False)
        if len(args)%2 == 0:
            part = int(len(args)/2)
            rel1 = rel[0:part]
            rel2 = rel[part:len(rel)]
            Q1 = Statistics.Median(rel1)
            Q2 = Statistics.Median(rel)
            Q3 = Statistics.Median(rel2)
            return [Q1,Q2,Q3]
        else:
            part = int(len(args)/2)
            rel1 = rel[0:part]
            rel2 = rel[part+1:len(rel)]
            Q1 = Statistics.Median(rel1)
            Q2 = Statistics.Median(rel)
            Q3 = Statistics.Median(rel2)
            return [Q1,Q2,Q3]

    def IQR(args) -> list:
        q = Statistics.Quartiles(args)
        iqr = q[len(q)-1]-q[0]
        return iqr

    def Outliers(args) -> list:
        q = Statistics.Quartiles(args)
        iqr = Statistics.IQR(args)
        args_range = [q[0]-1.5*iqr,q[len(q)-1]+1.5*iqr]
        out = []
        for i in range(0,len(args)):
            if args[i]>=args_range[0]:
                if args[i]<=args_range[1]:
                    pass
                else:
                    out.append(args[i])
            else:
                out.append(args[i])
        if out == []:
            return None
        else:
            return out

    def Absolute(num) -> int:
        """
        Absolute value or Modulus Value both are functions that always gives positive number no matter what kind of integer you are giving as an input\n
        Denoted as `|x|`\n

        for more info: <https://www.google.com/search?q=absolute+value>\n

        ===========================\n
        Mathematical Representation\n
        ===========================\n
        `|x| = {x; if x >= 0, -x; if x < 0}`
        """
        if num >= 0:
            return num
        elif num < 0:
            return num*(-1)
        else:
            return "Invalid input"

    def Mean(args) -> list:
        """
        Its gives an average value form a given datasets\n
        Dentnoted as `x̄`\n

        for more info: <https://www.google.com/search?q=mean>\n

        ===========================\n
        Mathematical Representation\n
        ===========================\n
        `x̄ = sum of the data/total number of the data`
        """
        return sum(args)/len(args)

    def RunningMean(args) -> list:
        """
        A moving average is a calculation to analyze data points by creating a series of averages of different subsets of the full data set.\n

        for more info: <https://www.google.com/search?q=running+mean>
        """
        avg = []
        i = 0
        size = 3
        while i < len(args)-size+1:
            w = args[i : i+size]
            s = sum(w)/size
            avg.append(s)
            i += 1
        return avg

    def HarmonicMean(args) -> list:
        """
        It is calculated by dividing the number of observations by the reciprocal of each number in the series.\n

        for more info: <https://www.google.com/search?q=harmonic+mean>
        """
        s = 0
        for i in range(0,len(args)):
            a = 1/(args[i])
            s += a
        return len(args)/s

    def GeometricMean(args) -> list:
        """
        The geometric mean is a mean or average, which indicates the central tendency or typical value of a set of numbers by using the product of their values\n

        for more info: <https://www.google.com/search?q=geometric+mean>\n

        ===========================\n
        Mathematical Representation\n
        ===========================\n
        GM1 = sqrt(ab)
        GM2 = cubert(abc)
        """
        p = 1
        for i in range(0,len(args)):
            a = args[i]
            p *= a
        return p**(1/len(args))

    def Mode(args) -> list:
        """
        It gives the number from a given set that repeats maximum times

        for more info: <https://www.google.com/search?q=mode>
        """
        return stats.mode(args)

    def Range(args) -> list:
        return max(args)-min(args)

    def Product(args) -> list:
        """
        It will multiply all the elements containing in the list
        """
        p = 1
        for i in range(0,len(args)):
            p *= args[i]
        return p

    def SquareSum(args) -> list:
        s = 0
        for i in range(0,len(args)):
            sq = args[i]**2
            s += sq
        return s

    def StandardDeviation(args) -> list:
        mean = round(sum(args)/len(args),3)
        rep = []
        for i in range(0,len(args)):
            a = (args[i]-mean)**2
            rep.append(a)
        total = sum(rep)
        return math.sqrt(total/(len(args)-1))

    def ZScore(args:list,num:int):
        m = Statistics.Mean(args)
        dev = Statistics.StandardDeviation(args)
        a = num-m
        return a/dev

    def Median(args) -> list:
        rel = sorted(args, reverse = False)
        if len(rel)%2 == 0:
            mid1 = int(len(rel)/2)
            mid2 = mid1-1
            return (rel[mid1]+rel[mid2])/2
        else:
            mid = int(len(rel)/2)
            return rel[mid]

    def MeanDeviation(args) -> list:
        mean = sum(args)/len(args)
        rep = []
        for i in range(0,len(args)):
            a = abs(args[i]-mean)
            rep.append(a)
        total = sum(rep)
        return total/len(args)

    def Percentile(args:list,n:int):
        if n in args:
            b = 0
            for i in range(0,len(args)):
                if n > args[i]:
                    b += 1
                else:
                    b += 0
            return (b/len(args))*100
        else:
            return f"Unexpected Input! {n} is not in {args}!"

    def MedianAvgDeviation(args) -> list:
        m = sum(args)/len(args)
        rel = []
        for i in range(0,len(args)):
            a = abs(args[i]-m)
            rel.append(a)
        mid = Statistics.Median(rel)
        return mid

    def CumSum(args) -> list:
        s = 0
        cumsum = []
        for i in range(0,len(args)):
            s += args[i]
            cumsum.append(s)
        return cumsum

    def SampleVariance(args) -> list:
        mean = round(sum(args)/len(args),3)
        rep = []
        for i in range(0,len(args)):
            a = (args[i]-mean)**2
            rep.append(a)
        total = sum(rep)
        return total/(len(args)-1)

    def PopulationVariance(args) -> list:
        mean = sum(args)/len(args)
        rep = []
        for i in range(0,len(args)):
            a = (args[i]-mean)**2
            rep.append(a)
        total = sum(rep)
        return total/(len(args))

    def RMS(args) -> list:
        rep = []
        for i in range(0,len(args)):
            a = args[i]**2
            rep.append(a)
        total = sum(rep)
        return math.sqrt(total/len(args))

    def LR(args,kwargs) -> list:
        if len(args) == len(kwargs):
            y = sum(kwargs)
            x = sum(args)
            xy = 0
            x2 = 0
            for i in range(0,len(args)):
                a = args[i]**2
                b = args[i]*kwargs[i]
                xy += b
                x2 += a
            N1 = y*x2-x*xy
            D1 = len(args)*x2-x**2
            intercept = N1/D1
            N2 = len(args)*xy-x*y
            D2 = len(args)*x2-x**2
            slope = N2/D2
            return [intercept,slope]
        else:
            return "Length of the both parameters should be euqal"

    def StandardError(args) -> list:
        dev = Statistics.StandardDeviation(args)
        return dev/math.sqrt(len(args))

    def RelativeFrequency(args) -> list:
        rel = []
        freq = {}
        for item in args:
            if item in freq:
                freq[item] += 1
            else:
                freq[item] = 1
        f = list(freq.values())
        for i in range(0,len(f)):
            r = f[i]/len(args)
            rel.append(r)
        return [freq,rel]

    def CorrelationCoefficient(args,kwargs) -> list:
        if len(args) == len(kwargs):
            y = sum(kwargs)
            x = sum(args)
            xy = 0
            x2 = 0
            y2 = 0
            for i in range(0,len(args)):
                a = args[i]**2
                b = args[i]*kwargs[i]
                c = kwargs[i]**2
                x2 += a
                xy += b
                y2 += c
            N = len(args)*xy-x*y
            D = math.sqrt((len(args)*x2-x**2)*(len(args)*y2-y**2))
            return N/D
        else:
            return "Length of the both parameters should be euqal"

    def CoefficientDetermination(args,kwargs) -> list:
        if len(args) == len(kwargs):
            x = sum(args)
            y = sum(kwargs)
            x2 = 0
            y2 = 0
            xy = 0
            for i in range(0,len(args)):
                a = args[i]**2
                b = args[i]*kwargs[i]
                c = kwargs[i]**2
                x2 += a
                y2 += c
                xy += b
            N = len(args)*xy-x*y
            D = math.sqrt((len(args)*x2-x**2)*(len(args)*y2-y**2))
            return round(N/D,3)
        else:
            return "Length of the both parameters should be euqal"

    def MeanSquaredError(actual,predicted) -> list:
        """
        The measure of how close a fitted line is to data points. For every data point,\n
        you take the distance vertically from the point to the corresponding y value on the curve fit (the error),\n
        and square the value\n

        for more info: <https://www.google.com/search?q=mean+squared+error>\n

        ===========================\n
        Mathematical Representation\n
        ===========================\n
        `(1/n)/summation((observed-predicted)^2)`

        `n` number of data points\n
        `observed` oberserved data points\n
        `predicted` predicte data points
        """
        if len(actual) == len(predicted):
            rel = []
            for i in range(0,len(actual)):
                a = (actual[i]-predicted[i])**2
                rel.append(a)
            return sum(rel)/len(actual)
        else:
            return "Length of both parameters are unequal"

    def MeanAbsoluteError(actual,predicted) -> list:
        if len(actual) == len(predicted):
            rel = []
            for i in range(0,len(actual)):
                a = Statistics.Absolute(actual[i]-predicted[i])
                rel.append(a)
            return sum(rel)/len(actual)
        else:
            return "Length of both parameters are unequal"


class Stack:
    def __init__(self):
        self.stack = []
    def push(self,item):
        self.stack.append(item)
    def pop(self):
        if len(self.stack) > 0:
            return self.stack.pop()
        else:
            return None
    def peek(self):
        if len(self.stack) > 0:
            return self.stack[len(self.stack)-1]
        else:
            return None
    def __str__(self):
        return str(self.stack)


def duplicates(nums):
    repeat = {}
    sort = sorted(nums,reverse = False)
    for i in sort:
        if sort.count(i) >= 1:
            repeat.update({i:sort.count(i)})
    return repeat


class BinaryConverter:
    def str2binary(args) -> str:
        l = []
        words = list(args)
        print(words)
        for i in range(0,len(words)):
            to_num = ord(words[i])
            to_bin = int(bin(to_num)[2:])
            l.append(to_bin)
        return l

    def str2hexadecimal(args) -> str:
        l = []
        words = list(args)
        print(words)
        for j in range(0,len(words)):
            to_num = ord(words[j])
            to_bin = hex(to_num)[2:]
            l.append(to_bin)
        return l

    def str2octadecimal(args) -> str:
        l = []
        words = list(args)
        print(words)
        for k in range(0,len(words)):
            to_num = ord(words[k])
            to_bin = int(oct(to_num)[2:])
            l.append(to_bin)
        return l

    def int2binary(args) -> (list|int):
        if type(args) == list:
            b = []
            for i in range(0,len(args)):
                item = bin(args[i])
                b.append(item[2:])
            return b
        elif type(args) == int:
            return bin(args)[2:]
        else:
            return "argument should be integer or list"

    def int2hexadecimal(args) -> (list|int):
        if type(args) == list:
            h = []
            for j in range(0,len(args)):
                item = hex(args[j])
                h.append(item[2:])
            return h
        elif type(args) == int:
            return hex(args)[2:]
        else:
            return "argument should be integer or list"

    def int2octadecimal(args) -> (list|int):
        if type(args) == list:
            o = []
            for k in range(0,len(args)):
                item = oct(args[k])
                o.append(item[2:])
            return o
        elif type(args) == int:
            return oct(args)[2:]
        else:
            return "argument should be integer or list"


class Length:
    def km2cm(km) -> int:
        return km*1e5

    def km2m(km) -> int:
        return km*1e3

    def km2mm(km) -> int:
        return km*1e6

    def km2um(km) -> int:
        return km*1e9

    def km2nm(km) -> int:
        return km*1e12

    def km2miles(km) -> int:
        return km/1.609

    def km2yard(km) -> int:
        return km*1093.61

    def km2ft(km) -> int:
        return km*3280.84

    def km2inch(km) -> int:
        return km*39370.1
    
    def km2nautical_miles(km) -> int:
        return km/1.852

    def m2km(m) -> int:
        return m/1e3

    def m2cm(m) -> int:
        return m*1e2
    
    def m2mm(m) -> int:
        return m*1e3

    def m2um(m) -> int:
        return m*1e6

    def m2nm(m) -> int:
        return m*1e9

    def m2miles(m) -> int:
        return m/1609

    def m2yard(m) -> int:
        return m*1.094

    def m2ft(m) -> int:
        return m*3.281

    def m2inch(m) -> int:
        return m*39.37

    def m2nautical_miles(m) -> int:
        return m/1852

    def cm2km(cm) -> int:
        return cm*1e-5

    def cm2m(cm) -> int:
        return cm*1e2

    def cm2mm(cm) -> int:
        return cm*1e0

    def cm2um(cm) -> int:
        return cm*1e4

    def cm2nm(cm) -> int:
        return cm*1e7

    def cm2miles(cm) -> int:
        return cm/160900

    def cm2yard(cm) -> int:
        return cm/91.44

    def cm2ft(cm) -> int:
        return cm/30.48

    def cm2inch(cm) -> int:
        return cm/2.54

    def cm2nautical_miles(cm) -> int:
        return cm*1e-5

    def mm2km(mm) -> int:
        return mm/1e6

    def mm2m(mm) -> int:
        return mm/1e3

    def mm2cm(mm) -> int:
        return mm/1e0

    def mm2um(mm) -> int:
        return mm/1e3

    def mm2nm(mm) -> int:
        return mm*1e6

    def mm2km(mm) -> int:
        return mm/1e6

    def mm2miles(mm) -> int:
        return mm/1.609e6

    def mm2yard(mm) -> int:
        return mm/914.4

    def mm2ft(mm) -> int:
        return mm/304.8

    def mm2inch(mm) -> int:
        return mm/25.4

    def mm2km(mm) -> int:
        return mm/1.852e6

    def um2km(um) -> int:
        return um/1e9

    def um2m(um) -> int:
        return um/1e6

    def um2cm(um) -> int:
        return um/1e4

    def um2mm(um) -> int:
        return um/1e3

    def um2nm(um) -> int:
        return um*1e3

    def um2miles(um) -> int:
        return um/1.609e9

    def um2yard(um) -> int:
        return um/914400

    def um2ft(um) -> int:
        return um/304800

    def um2inch(um) -> int:
        return um/25400

    def um2nautical_miles(um) -> int:
        return um/1.852e9

    def nm2km(nm) -> int:
        return nm/1e12

    def nm2m(nm) -> int:
        return nm/1e9

    def nm2cm(nm) -> int:
        return nm/1e7

    def nm2mm(nm) -> int:
        return nm/1e6

    def nm2um(nm) -> int:
        return nm/1e3

    def nm2miles(nm) -> int:
        return nm/1.609e12

    def nm2yard(nm) -> int:
        return nm/9.144e8

    def nm2ft(nm) -> int:
        return nm/3.048e8

    def nm2inch(nm) -> int:
        return nm/2.54e7

    def nm2nuatical_miles(nm) -> int:
        return nm/1.852e12

    def miles2km(miles) -> int:
        return miles*1.609

    def miles2m(miles) -> int:
        return miles*1609

    def miles2cm(miles) -> int:
        return miles*160900

    def miles2mm(miles) -> int:
        return miles*1.609e6

    def miles2um(miles) -> int:
        return miles*1.609e9

    def miles2nm(miles) -> int:
        return miles*1.609e12

    def miles2yard(miles) -> int:
        return miles*1760

    def miles2ft(miles) -> int:
        return miles*5280

    def miles2inch(miles) -> int:
        return miles*63360

    def miles2nautical_miles(miles) -> int:
        return miles/1.151

    def yard2km(yard) -> int:
        return yard/1094

    def yard2m(yard) -> int:
        return yard/1.094
    
    def yard2cm(yard) -> int:
        return yard/10.94

    def yard2mm(yard) -> int:
        return yard/109.4

    def yard2um(yard) -> int:
        return yard*914400

    def yard2nm(yard) -> int:
        return yard*9.144e8

    def yard2miles(yard) -> int:
        return yard/1760

    def yard2ft(yard) -> int:
        return yard*3

    def yard2inch(yard) -> int:
        return yard*36

    def yard2nautical_miles(yard) -> int:
        return yard/2025

    def ft2km(ft) -> int:
        return ft/3281

    def ft2m(ft) -> int:
        return ft/3.281

    def ft2cm(ft) -> int:
        return ft*30.48

    def ft2mm(ft) -> int:
        return ft*304.8

    def ft2um(ft) -> int:
        return ft*304800

    def ft2nm(ft) -> int:
        return ft*3.048e8

    def ft2miles(ft) -> int:
        return ft/5280

    def ft2yard(ft) -> int:
        return ft/3

    def ft2inch(ft) -> int:
        return ft*12

    def ft2nautical_miles(ft) -> int:
        return ft/6076

    def inch2km(inch) -> int:
        return inch/39370

    def inch2m(inch) -> int:
        return inch/39.37

    def inch2cm(inch) -> int:
        return inch*2.54

    def inch2mm(inch) -> int:
        return inch*25.4

    def inch2um(inch) -> int:
        return inch*25400

    def inch2nm(inch) -> int:
        return inch*2.54e7

    def inch2miles(inch) -> int:
        return inch/63360

    def inch2yard(inch) -> int:
        return inch/36

    def inch2ft(inch) -> int:
        return inch/12

    def inch2nautical_miles(inch) -> int:
        return inch/72910

    def nautical_miles2km(nautical_miles) -> int:
        return nautical_miles*1.852
    
    def nautical_miles2m(nautical_miles) -> int:
        return nautical_miles*1852

    def nautical_miles2cm(nautical_miles) -> int:
        return nautical_miles*185200

    def nautical_miles2mm(nautical_miles) -> int:
        return nautical_miles*1.852e6

    def nautical_miles2um(nautical_miles) -> int:
        return nautical_miles*1.852e9

    def nautical_miles2nm(nautical_miles) -> int:
        return nautical_miles*1.852e12

    def nautical_miles2miles(nautical_miles) -> int:
        return nautical_miles*1.151

    def nautical_miles2yard(nautical_miles) -> int:
        return nautical_miles*2025

    def nautical_miles2ft(nautical_miles) -> int:
        return nautical_miles*6076

    def nautical_miles2inch(nautical_miles) -> int:
        return nautical_miles*72910


class Pressure:
    def bar2pascal(bar) -> int:
        return bar*1e5

    def bar2psi(bar) -> int:
        return bar*14.504

    def bar2atm(bar) ->int:
        return bar/1.013

    def bar2torr(bar) -> int:
        return bar*750.1

    def pascal2bar(pascal) -> int:
        return pascal/1e5

    def pascal2psi(pascal) -> int:
        return pascal/6895

    def pascal2atm(pascal) -> int:
        return pascal/101300

    def pascal2torr(pascal) -> int:
        return pascal*133.3

    def psi2bar(psi) -> int:
        return psi/14.504

    def psi2pascal(psi) -> int:
        return psi*6895

    def psi2atm(psi) -> int:
        return psi/14.696

    def psi2torr(psi) -> int:
        return psi*51.715

    def atm2bar(atm) -> int:
        return atm*1.013

    def atm2pascal(atm) -> int:
        return atm*101300

    def atm2psi(atm) -> int:
        return atm*14.696

    def atm2torr(atm) -> int:
        return atm*760

    def torr2bar(torr) -> int:
        return torr/750.1

    def torr2pascal(torr) -> int:
        return torr*133.3

    def torr2psi(torr) -> int:
        return torr/51.715

    def torr2atm(torr) -> int:
        return torr/760


class Angle:
    def deg2rad(deg) -> int:
        return deg*math.pi/180

    def deg2grad(deg) -> int:
        return deg*200/180

    def deg2mili_rad(deg) -> int:
        return deg*1000*math.pi/180

    def deg2min_arc(deg) -> int:
        return deg*60

    def deg2sec_arc(deg) -> int:
        return deg*3600

    def rad2deg(rad) -> int:
        return rad*180/math.pi

    def rad2grad(rad) -> int:
        return rad*200/math.pi

    def rad2mili_rad(rad) -> int:
        return rad*1000

    def rad2min_arc(rad) -> int:
        return rad*10800/math.pi

    def rad2sec_arc(rad) -> int:
        return rad*648000/math.pi

    def grad2deg(grad) -> int:
        return grad*180/200

    def grad2rad(grad) -> int:
        return grad*math.pi/200

    def grad2mili_rad(grad) -> int:
        return grad*1000*math.pi/200

    def grad2min_arc(grad) -> int:
        return grad*54

    def grad2sec_arc(grad) -> int:
        return grad*3240

    def mili_rad2deg(mili_rad) -> int:
        return mili_rad*180/math.pi*1000

    def mili_rad2rad(mili_rad) -> int:
        return mili_rad/1000

    def mili_grad(mili_rad) -> int:
        return mili_rad*200/1000*math.pi

    def mili_rad2min_arc(mili_rad) -> int:
        return mili_rad*10800/1000*math.pi

    def mili_rad2sec_arc(mili_rad) -> int:
        return mili_rad*648000/1000*math.pi

    def min_arc2deg(min_arc) -> int:
        return min_arc/60

    def min_arc2rad(min_arc) -> int:
        return min_arc*math.pi/10800

    def min_arc2grad(min_arc) -> int:
        return min_arc/54

    def min_arc2mili_rad(min_arc) -> int:
        return min_arc*1000*math.pi/10800

    def min_arc2sec_arc(min_arc) -> int:
        return min_arc*60

    def sec_arc2deg(sec_arc) -> int:
        return sec_arc/3600

    def sec_arc2rad(sec_arc) -> int:
        return sec_arc*math.pi/648000

    def sec_arc2grad(sec_arc) -> int:
        return sec_arc/3240

    def sec_arc2mili_rad(sec_arc) -> int:
        return sec_arc*1000*math.pi/648000

    def sec_arc2min_arc(sec_arc) -> int:
        return sec_arc/60


class Time:
    def nanoseconds2microseconds(nsec) -> int:
        return nsec/1e3

    def nanoseconds2miliseconds(nsec) -> int:
        return nsec/1e6

    def nanoseconds2seconds(nsec) -> int:
        return nsec/1e9

    def nanoseconds2minutes(nsec) -> int:
        return nsec/6e10

    def nanoseconds2hours(nsec) -> int:
        return nsec/3.6e12

    def nanoseconds2days(nsec) -> int:
        return nsec/8.64e13

    def nanoseconds2weeks(nsec) -> int:
        return nsec/6.048e14

    def nanoseconds2months(nsec) -> int:
        return nsec/2.628e15

    def nanoseconds2years(nsec) -> int:
        return nsec/3.154e16

    def nanoseconds2decades(nsec) -> int:
        return nsec/3.154e17

    def nanoseconds2century(nsec) -> int:
        return nsec/3.154e18

    def microseconds2nanoseconds(usec) -> int:
        return usec*1e3

    def microseconds2miliseconds(usec) -> int:
        return usec/1e3

    def microseconds2seconds(usec) -> int:
        return usec/1e6

    def microseconds2minutes(usec) -> int:
        return usec/6e7

    def microseconds2hours(usec) -> int:
        return usec/3.6e9

    def microseconds2days(usec) -> int:
        return usec/8.64e10

    def microseconds2weeks(usec) -> int:
        return usec/6.048e11

    def microseconds2months(usec) -> int:
        return usec/2.628e12

    def microseconds2years(usec) -> int:
        return usec/3.154e13

    def microseconds2decades(usec) -> int:
        return usec/3.154e14

    def microseconds2century(usec) -> int:
        return usec/3.154e15

    def miliseconds2nanoseconds(msec) -> int:
        return msec*1e6

    def miliseconds2microseconds(msec) -> int:
        return msec*1e3

    def miliseconds2seconds(msec) -> int:
        return msec/1e3

    def miliseconds2minutes(msec) -> int:
        return msec/6e4

    def miliseconds2hours(msec) -> int:
        return msec/3.6e6

    def miliseconds2days(msec) -> int:
        return msec/8.64e7

    def miliseconds2weeks(msec) -> int:
        return msec/6.048e8

    def miliseconds2months(msec) -> int:
        return msec/2.628e9

    def miliseconds2years(msec) -> int:
        return msec/3.154e10

    def miliseconds2decades(msec) -> int:
        return msec/3.154e11

    def miliseconds2century(msec) -> int:
        return msec/3.154e12

    def seconds2nanoseconds(sec) -> int:
        return sec*1e9

    def seconds2microseconds(sec) -> int:
        return sec*1e6
    
    def seconds2miliseconds(sec) -> int:
        return sec*1e3

    def seconds2minuntes(sec) -> int:
        return sec/60

    def seconds2hours(sec) -> int:
        return sec/3600

    def seconds2days(sec) -> int:
        return sec/86400

    def seconds2weeks(sec) -> int:
        return sec/604800

    def seconds2months(sec) -> int:
        return sec/2.628e6

    def seconds2years(sec) -> int:
        return sec/3.154e7

    def seconds2decade(sec) -> int:
        return sec/3.154e8

    def seconds2century(sec) -> int:
        return sec/3.154e9

    def minutes2nanoseconds(min) -> int:
        return min*6e10

    def minutes2microseconds(min) -> int:
        return min*6e7

    def minutes2miliseconds(min) -> int:
        return min*6e4

    def minutes2seconds(min) -> int:
        return min*60

    def minutes2hours(min) -> int:
        return min/60

    def minutes2days(min) -> int:
        return min/1440

    def minutes2weeks(min) -> int:
        return min/10080

    def minutes2months(min) -> int:
        return min/43800

    def minutes2years(min) -> int:
        return min/525600

    def minutes2decade(min) -> int:
        return min/5.256e6

    def minutes2century(min) -> int:
        return min/5.256e7

    def hours2nanoseconds(hr) -> int:
        return hr*3.6e12

    def hours2microseconds(hr) -> int:
        return hr*3.6e9

    def hours2miliseconds(hr) -> int:
        return hr*3.6e6

    def hours2seconds(hr) -> int:
        return hr*3600

    def hours2hours(hr) -> int:
        return hr*60

    def hours2days(hr) -> int:
        return hr/24

    def hours2weeks(hr) -> int:
        return hr/168

    def hours2months(hr) -> int:
        return hr/730

    def hours2years(hr) -> int:
        return hr/8760

    def hours2decades(hr) -> int:
        return hr/87600

    def hours2century(hr) -> int:
        return hr/876000

    def days2nanoseconds(days) -> int:
        return days*8.63e13

    def days2microseconds(days) -> int:
        return days*8.63e10

    def days2miliseconds(days) -> int:
        return days*8.63e7

    def days2seconds(days) -> int:
        return days*86400

    def days2minutes(days) -> int:
        return days*1440

    def days2hours(days) -> int:
        return days*24

    def days2weeks(days) -> int:
        return days/7

    def days2months(days) -> int:
        return days/30.417

    def days2years(days) -> int:
        return days/365

    def days2decades(days) -> int:
        return days*3650

    def days2century(days) -> int:
        return days*36500

    def weeks2nanoseconds(weeks) -> int:
        return weeks*6.048e14

    def weeks2microseconds(weeks) -> int:
        return weeks*6.048e11

    def weeks2miliseconds(weeks) -> int:
        return weeks*6.048e8

    def weeks2seconds(weeks) -> int:
        return weeks*604800

    def weeks2minutes(weeks) -> int:
        return weeks*10080

    def weeks2hours(weeks) -> int:
        return weeks*168

    def weeks2days(weeks) -> int:
        return weeks*7

    def weeks2months(weeks) -> int:
        return weeks/4.345

    def weeks2years(weeks) -> int:
        return weeks/52.143

    def weeks2decades(weeks) -> int:
        return weeks/521.4

    def weeks2century(weeks) -> int:
        return weeks/5214

    def months2nanoseconds(months) -> int:
        return months*2.628e15

    def months2microseconds(months) -> int:
        return months*2.628e12

    def months2miliseconds(months) -> int:
        return months*2.628e9
    
    def months2seconds(months) -> int:
        return months*2.628e6

    def months2minutes(months) -> int:
        return months*43800

    def months2hours(months) -> int:
        return months*730

    def months2days(months) -> int:
        return months*30.417

    def months2weeks(months) -> int:
        return months*4.345

    def months2years(months) -> int:
        return months/12

    def months2decades(months) -> int:
        return months/120

    def months2century(months) -> int:
        return months/1200

    def years2nanoseconds(yrs) -> int:
        return yrs*3.154e16

    def years2microseconds(yrs) -> int:
        return yrs*3.154e13

    def years2miliseconds(yrs) -> int:
        return yrs*3.154e10

    def years2seconds(yrs) -> int:
        return yrs*3.154e7

    def years2minutes(yrs) -> int:
        return yrs*525600

    def years2hours(yrs) -> int:
        return yrs*8760

    def years2days(yrs) -> int:
        return yrs*365

    def years2weeks(yrs) -> int:
        return yrs*52.143

    def years2months(yrs) -> int:
        return yrs*12

    def years2decades(yrs) -> int:
        return yrs/10

    def years2century(yrs) -> int:
        return yrs/100

    def decades2nanoseconds(decades) -> int:
        return decades*3.154e17

    def decades2microseconds(decades) -> int:
        return decades*3.154e14

    def decades2miliseconds(decades) -> int:
        return decades*3.154e11

    def decades2seconds(decades) -> int:
        return decades*3.154e8

    def decades2minutes(decades) -> int:
        return decades*5.256e6

    def decades2hours(decades) -> int:
        return decades*87600

    def decades2days(decades) -> int:
        return decades*3650

    def decades2weeks(decades) -> int:
        return decades*521.4

    def decades2months(decades) -> int:
        return decades*120

    def decades2years(decades) -> int:
        return decades*10

    def decades2century(decades) -> int:
        return decades/10
    
    def century2nanoseconds(century) -> int:
        return century*3.154e18

    def century2microseconds(century) -> int:
        return century*3.154e15

    def century2miliseconds(century) -> int:
        return century*3.154e12

    def century2seconds(century) -> int:
        return century*3.154e9

    def century2minutes(century) -> int:
        return century*5.256e7

    def century2hours(century) -> int:
        return century*876000

    def century2days(century) -> int:
        return century*36500

    def century2weeks(century) -> int:
        return century*5214

    def century2months(century) -> int:
        return century*1200

    def century2years(century) -> int:
        return century*100

    def century2decades(century) -> int:
        return century*10


class Temperature:
    def c2k(celcius) -> int:
        if celcius >= -273.15 and celcius <= 1.417e32:
            k = celcius+273.15
            return round(k,2)
        else:
            raise ValueError("Temperature below -273.15 and above 1.417*10^32 Celcius is not possible")

    def c2f(celcius) -> int:
        if celcius >= -273.15 and celcius <= 1.417e32:
            f = round((celcius*1.8)+32,2)
            return round(f,2)
        else:
            raise ValueError("Temperature below -273.15 and above 1.417*10^32 celcius is not possible")

    def k2c(kelvin) -> int:
        if kelvin >= 0 and kelvin <= 1.417e32:
            c = kelvin-273.15
            return round(c,2)
        else:
            raise ValueError("Temperature below 0 and above 1.417*10^32 kelvin is not possible")

    def k2f(kelvin) -> int:
        if kelvin >= 0 and kelvin <= 1.417e32:
            f = ((kelvin-273.15)*1.8)+32
            return round(f,2)
        else:
            raise ValueError("Temperature below 0 and above 1.417*10^32 kelvin is not possible")

    def f2c(fahrenheit) -> int:
        if fahrenheit >= -459.67 and fahrenheit <= 2.55e32:
            c = round((fahrenheit-32)*0.55,2)
            return round(c,2)
        else:
            raise ValueError("Temperature below -459.67 and above 2.55*10^(32) fahrenheit is not possible")

    def f2k(fahrenheit) -> int:
        if fahrenheit >= -459.67 and fahrenheit <= 2.55e32:
            k = ((fahrenheit-32)*5/9)+273.15
            return round(k,2)
        else:
            raise ValueError("Temperature below -459.67 and above 2.55*10^(32) fahrenheit is not possible")


class DistanceFormula:
    """
    x,y,z: int
    """

    def Distance2d(x1,x2,y1,y2) -> int:
        d = math.sqrt((x2-x1)**2+(y2-y1)**2)
        return f"{round(d,2)} units"

    def Distance3d(x1,x2,y1,y2,z1,z2) -> int:
        d = math.sqrt((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)
        return f"{round(d,2)} units"


class SectionFormula:
    """
    x,y,z: int
    """

    def Section2d(x1,x2,y1,y2,n,m) -> int:
        x = x1*m+x2*n
        y = y1*m+y2*n
        ratio = n+m
        return f"{x}/{ratio},{y}/{ratio}"

    def Section3d(x1,x2,y1,y2,z1,z2,n,m) -> int:
        x = x1*m+x2*n
        y = y1*m+y2*n
        z = z1*m+z2*n
        ratio = n+m
        return f"{x}/{ratio},{y}/{ratio},{z}/{ratio}"


class Area:
    def Circle(radius) -> int:
        return f"{round(pi.value*radius**2,2)} sqr units"

    def Square(sides) -> int:
        return f"{round(sides**2,2)} sqr units"

    def Rhombus(diagonal_1,diagonal_2) -> int:
        return f"{round(diagonal_1*diagonal_2*0.5,2)} units"

    def Reactangle(length,breadth) -> int:
        return f"{round(length*breadth,2)} sqr units"

    def Parallelogram(length,breadth) -> int:
        return f"{round(length*breadth,2)} sqr units"

    def Triangle(height,base) -> int:
        return f"{round(0.5*height*base,2)} sqr units"

    def Equilateral_triangle(side) -> int:
        deg = np.deg2rad(60)
        return f"{round(0.5*trigo.sin(deg)*side**2,2)} sqr units"

    def Ellipse(a,b) -> int:
        return f"{round(pi.value*a*b,2)} sqr units"

    def Trapezium(a,b,height) -> int:
        return f"{((a+b)*0.5)*height} sqr units"

    def Sector(angle,radius) -> int:
        return f"{(angle/360)*pi.value*radius**2} sqr units"
    

class Perimeter:
    def Circle(radius) -> int:
        return f"{round(2*pi.value*radius,2)} units"

    def Square(side) -> int:
        return f"{round(4*side,2)} units"

    def Rhombus(side) -> int:
        return f"{round(4*side,2)} units"

    def Rectangle(length,breadth) -> int:
        return f"{round(2*(length+breadth),2)} units"

    def Parallelogram(length,breadth) -> int:
        return f"{round(2*(length+breadth),2)}"

    def Triangle(side1,side2,side3) -> int:
        p = side1+side2+side3
        return f"{round(p,2)} units"

    def Ellipse(a,b) -> int:
        p = (2*pi.value)*math.sqrt(a**2*b**2*0.5)
        return f"{round(p,3)} units"

    def Trapezium(a,b,c,d) -> int:
        return f"{a+b+c+d} units"

    def Sector(radius,angle) -> int:
        return f"{round((2*radius)+((angle/360)*2*pi.value*radius),2)} units"


class Volume:
    def Cube(side) -> int:
        return f"{round(side**3,2)} units cube"

    def Cuboid(length,breadth,height) -> int:
        return f"{round(length*breadth*height,2)} units cube"

    def Cylinder(radius,height) -> int:
        return f"{round(pi.value*radius**2*height,2)} units cube"

    def Prism(length,breadth,Height) -> int:
        return f"{round(length*breadth*Height,2)} units cube"

    def Sphere(radius) -> int:
        return f"{round((4/3)*pi.value*radius**3,2)} units cube"

    def Pyramid(length,breadth,Height) -> int:
        return f"{round((1/3)*length*breadth*Height,2)} units cube"

    def RightCircularCone(radius,height) -> int:
        return f"{round((1/3)*pi.value*radius**2*height,2)} units cube"

    def QuadBasePyramid(length,width,height) -> int:
        return f"{round((1/3)*pi.value*length*width*height,2)} units cube"

    def Ellipsoid(x,y,z) -> int:
        return f"{round((4/3)*pi.value*x*y*z,2)} units cube"


    # NOTE! #

    """
        We are assuming the side of the polyhedron are same or
        we can say regular polyhedron
    """
    
    def Tetrahedron(side) -> int:
        return f"{round((side**3)*6*math.sqrt(2),2)} units cube"

    def Octahedron(side) -> int:
        return f"{round((math.sqrt(2)/3)*side**3,2)}"

    def Dodecahedron(side) -> int:
        return f"{round(((15+7*math.sqrt(5))/4)*side**3,2)} units cube"


class PeriodicTable:
    def table():
        return ("""

                 1  2  3   4  5  6  7  8  9  10 11 12 13 14 15 16 17 18
            1    H                                                   He
            2    Li Be                                B  C  N  O  F  Ne
            3    Na Mg                                Al Si P  S  Cl Ar
            4    K  Ca Sc  Ti V  Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr
            5    Rb Sr Y   Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I  Xe
            6    Cs Be La- Hf Ta W  Re Os Ir Pt Au Hg Tl Pd Bi Po At Rn
            7    Fr Ra Ac- Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og

                          -Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu
                          -Th Pa U  Np Pu Am Cm Bk Cf Es Fm Md No Lr

                """)

    def spdf():
        return ("""
                1s
                2s 2p
                3s 3p 3d
                4s 4p 4d 4f
                5s 5p 5d 5f
                6s 6p 6d
                7s 7p

                s orbital can have -> [1 to 2] electrons
                p orbital can have -> [1 to 6] electrons
                d orbital can have -> [1 to 10] electrons
                f orbital can have -> [1 to 14] electrons

                """)


    def symbol(symbol_) -> str:
        position = data.index[data["Symbol"].str.lower() == symbol_.lower()].tolist()[0]
        return data.iloc[position]

    def element(element_name) -> str:
        position = data.index[data["Element"].str.lower() == element_name.lower()].tolist()[0]
        return data.iloc[position]

    def atomic_number(atomic_number) -> int:
        return data.iloc[atomic_number-1]


class Chemistry:
    def HalfLifeZeroOrder(Ao,k) -> int:
        """
            Ao(Initial Concentration): int
            k(Rate Constant): int
        """
        t = Ao/(2*k)
        return f"{round(t,2)} yrs"

    def HalfLifeFirstOrder(k) -> int:
        """
            k(Rate Constant): int
        """
        t = 0.693/(2*k)
        return f"{round(t,2)} yrs"

    def HalfLifeThirdOrder(Ao,k) -> int:
        """
            Ao(Initial Concentration): int
            k(Rate Constant): int
        """
        t = 1/(Ao*k)
        return f"{round(t,2)} yrs"

    """
    P(Concetration on produt): int
    R(Conetration on reactant): int
    std_potential(Standard Potential): int
    """

    def NernstEquation(P,R,n,std_potential) -> int:
        E = std_potential - (0.06/n)*math.log10(R/P)
        return f"{round(E,2)} Volts"

    """
    oxdn(oxidation): int
    redn(redution): int
    """

    def StdPotential(oxdn,redn) -> int:
        E = redn-oxdn
        return f"{E} Volts"

    def MassPercent(mass_solute,mass_solution) -> int:
        M = (mass_solute/mass_solution)*100
        return M


class LogicGates:

            #TRUTH TABLE#

    """
        AND =>  A | B | y = a.b
                0 | 0 | 0
                0 | 1 | 0
                1 | 0 | 0
                1 | 1 | 1

        OR =>   a | b | y = a+b
                0 | 0 | 0
                0 | 1 | 1
                1 | 0 | 1
                1 | 1 | 1
                
        XOR =>  a | b | y = a(+)b
                0 | 0 | 0
                0 | 1 | 1
                1 | 0 | 1
                1 | 1 | 0

        NAND => a | b | y = bar(a.b)
                0 | 0 | 1
                0 | 1 | 1
                1 | 0 | 1
                1 | 1 | 0

        NOR =>  a | b | y = bar(a+b)
                0 | 0 | 1
                0 | 1 | 0
                1 | 0 | 0
                1 | 1 | 0

        XNOR => a | b | y = a(+)b
                0 | 0 | 1
                0 | 1 | 0
                1 | 0 | 0
                1 | 1 | 1

        NOT =>  a | y = bar(a)
                0 | 1
                1 | 0
    """

    def AND(a,b):
        if a == 1 and b == 1:
            return True
        else:
            return False

    def OR(a,b):
        if a == 1 or b == 1:
            return True
        else:
            return False

    def XOR(a,b):
        if a != b:
            return True
        else:
            return False

    def NAND(a,b):
        if a == 1 and b == 1:
            return False
        else:
            return True

    def NOR(a,b):
        if a == 0 and b == 0:
            return True
        elif a == 1 and b == 0:
            return False
        elif a == 0 and b == 1:
            return False
        elif a == 1 and b == 1:
            return False

    def XNOR(a,b):
        if a == b:
            return True
        else:
            return False

    def NOT(a):
        not_gate = not a
        return not_gate


class LogarithmicFunction:
    def log_e(x) -> int:
        ln = np.log(x)
        return round(ln,3)

    def log_10(x) -> int:
        log = np.log10(x)
        return round(log,3)


class Trigonometry:

    # Degrees

    def sin_deg(angle) -> int:
        deg = np.deg2rad(angle)
        return round(trigo.sin(deg),2)

    def cos_deg(angle) -> int:
        deg = np.deg2rad(angle)
        return round(trigo.cos(deg),2)

    def tan_deg(angle) -> int:
        deg = np.deg2rad(angle)
        return round(trigo.tan(deg),2)

    def sec_deg(angle) -> int:
        deg = np.deg2rad(angle)
        return round(trigo.sec(deg),2)

    def cosec_deg(angle) -> int:
        deg = np.deg2rad(angle)
        return round(trigo.cosec(deg),2)

    def cot_deg(angle) -> int:
        deg = np.deg2rad(angle)
        return round(trigo.cot(deg),2)

    # Radians

    def sin_rad(angle) -> int:
        return round(trigo.sin(angle),2)

    def cos_rad(angle) -> int:
        return round(trigo.cos(angle),2)

    def tan_rad(angle) -> int:
        return round(trigo.tan(angle),2)

    def sec_rad(angle) -> int:
        return round(trigo.sec(angle),2)

    def cosec_rad(angle) -> int:
        return round(trigo.cosec(angle),2)

    def cot_rad(angle) -> int:
        return round(trigo.cot(angle),2)

class InversTrigonometry:
    
    def arcsine_rad(num) -> int:
        angle = trigo.arc_sin(num)
        return angle

    def arccos_rad(num) -> int:
        angle = trigo.arc_cos(num)
        return angle

    def arctan_rad(num) -> int:
        angle = trigo.arc_tan(num)
        return angle

    def arccosec_rad(num) -> int:
        angle = trigo.arc_cosec(num)
        return angle

    def arcsec_rad(num) -> int:
        angle = trigo.arc_sec(num)
        return angle

    def arccot_rad(num) -> int:
        angle = trigo.arc_cot(num)
        return angle

class Matrix:
    def Matrices(matrix:list,dimension:tuple): #--> Row,Column
        dimension = tuple(dimension)
        try:
            m = np.matrix(matrix).reshape((dimension))
            return m
        except ValueError as error:
            return error

    def Transpose(matrix) -> int:
        return matrix.T

    def Product(X,Y) -> int:
        # Note! #

        """
            The number of columns of a first matrix,
            should be equal to the number of rows
            of a second matrix.
        """
        return np.dot(X,Y)


    # NOTE #

    """
        For addition, subtractions the number of rows and columns
        for matrices should be equal!
        e.g => [[1,2,3],        [[9,8,7,6,5],
                [4,5,6]]         [34,56,87,98],
                                 [12,26,31,65]]

                (2,3)                (3,4)

        And for Determinant and Invverse of a matrices the number of
        rows and columns should be same!
        e.g => [[1,2,3],    [[0,9,8],
                [4,5,6],     [7,6,5],
                [7,8,9]]     [4,3,2]]
                     
                (3,3)           (3,3)
    """

    def Addition(X,Y) -> int:
        try:
            return np.add(X,Y)
        except ValueError as error:
            return error

    def Substraction(X,Y) -> int:
        try:
            return np.subtract(X,Y)
        except ValueError as error:
            return error
    
    def InverseMatrix(X) -> int:
        try:
            return np.linalg.inv(X)
        except np.linalg.LinAlgError as error:
            return error

    def Determinant(X) -> int:
        try:
            return np.linalg.det(X)
        except np.linalg.LinAlgError as error:
            return error


class Sets:
    def Sets(A) -> int:
        return set(A)

    def Union(A,B) -> int:
        return set.union(A,B)

    def Intersections(A,B) -> int:
        return set.intersection(A,B)


class Vectors:
    def toVector(x1,y1,z1,x2,y2,z2) -> int:
        x = x2-x1
        y = y2-y1
        z = z2-z1
        return f"{x}i,{y}j,{z}k"

    def ScalarMagnitude(i,j,k) -> int:
        m = math.sqrt(i**2+j**2+k**2)
        return f"{round(m,2)}"

    def DotProduct(x1,y1,z1,x2,y2,z2) -> int:
        x = x1*x2
        y = y1*y2
        z = z1*z2
        return f"{x+y+z}"

    def UnitVector(i,j,k) -> int:
        mag = math.sqrt(i**2+j**2+k**2)
        return f"{i}/{round(mag,1)}i,{j}/{round(mag,1)}j,{k}/{round(mag,1)}k"

    def CrossProduct(i1,j1,k1,i2,j2,k2) -> int:
        arr = np.array([[i1],[j1],[k1],
                        [i2],[j2],[k2]])

        a = arr[1][0]*arr[5][0]-arr[4][0]*arr[2][0]
        b = arr[0][0]*arr[5][0]-arr[3][0]*arr[2][0]
        c = arr[0][0]*arr[4][0]-arr[3][0]*arr[1][0]
        return f"({a})i,-({b})j,({c})k"

    def VectorMagnitude(i1,j1,k1,i2,j2,k2) -> int:
        arr = np.array([[i1],[j1],[k1],
                        [i2],[j2],[k2]])

        i = arr[1][0]*arr[5][0]-arr[4][0]*arr[2][0]
        j = arr[0][0]*arr[5][0]-arr[3][0]*arr[2][0]
        k = arr[0][0]*arr[4][0]-arr[3][0]*arr[1][0]
        m = math.sqrt(i**2+j**2+k**2)

        return round(m,2)







# Details
VERSION = "1.5.4"
AUTHOR = "Sahil Rajwar"
LINK = "https://github.com/Sahil-Rajwar-2004/chemaphy"
EMAIL = "justsahilrajwar2004@gmail.com"
