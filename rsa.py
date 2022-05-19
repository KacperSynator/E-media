from Crypto.Util.number import getPrime, inverse
import math


class MyRSA:
    def __init__(self, number_of_bits=1024):
        self._mod, self._pub_exp, self._pvt_exp = self.generate_keys()

    def generate_keys(self, number_of_bits=1024):
        p = getPrime(number_of_bits)
        q = getPrime(number_of_bits)
        n = p * q
        lcm = math.lcm(p-1, q-1)
        e = MyRSA.random_coprime_below(lcm, number_of_bits // 2)
        d = inverse(e, lcm)
        return n, e, d

    def encrypt(self, value):
        return pow(value, self._pub_exp, self._mod)

    def decrypt(self, value):
        return pow(value, self._pvt_exp, self._mod)

    @staticmethod
    def random_coprime_below(max_val, number_of_bits):
        result = getPrime(number_of_bits)
        while result >= max_val or math.gcd(result, max_val) != 1:
            result = getPrime(number_of_bits)
        return result
