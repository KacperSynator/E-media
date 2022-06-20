from Crypto.Util.number import getPrime, inverse
import math


class MyRSA:
    def __init__(self, number_of_bits=1024, generate_keys=False):
        if generate_keys:
            self._mod, self._pub_exp, self._pvt_exp = self.generate_keys(number_of_bits)
        self._num_bits = number_of_bits

    @property
    def num_bytes(self):
        return self._num_bits // 8

    @property
    def pub_exp(self):
        return self._pub_exp

    @property
    def pvt_exp(self):
        return self._pvt_exp

    @property
    def mod(self):
        return self._mod

    @property
    def keys(self):
        return self._mod, self._pub_exp, self.pvt_exp

    def set_keys(self, mod, pub_exp, pvt_exp):
        self._mod, self._pub_exp, self._pvt_exp = mod, pub_exp, pvt_exp

    @staticmethod
    def generate_keys(number_of_bits=1024):
        p = getPrime(number_of_bits // 2)
        q = getPrime(number_of_bits // 2)
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
