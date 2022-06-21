from rsa import MyRSA, PyRSA
import unittest
from random import randint
import abc


class BlockCipher(metaclass=abc.ABCMeta):
    padding_len = 3  # must be >= 2

    @staticmethod
    def encrypt(rsa, data, encrypt_func, padding=True):
        padding_len = BlockCipher.padding_len if padding else 0
        beg_idx, end_idx = 0, rsa.num_bytes - padding_len
        result = bytearray()
        while beg_idx < len(data):
            result += encrypt_func(rsa, data[beg_idx: end_idx])
            beg_idx = end_idx
            end_idx += rsa.num_bytes - padding_len
        return result

    @staticmethod
    def decrypt(rsa, data, decrypt_func):
        beg_idx, end_idx = 0, rsa.num_bytes
        result = bytearray()
        while beg_idx < len(data):
            result += decrypt_func(rsa, data[beg_idx: end_idx])
            beg_idx = end_idx
            end_idx += rsa.num_bytes
        return result

    @staticmethod
    @abc.abstractmethod
    def _encrypt(rsa, data):
        pass

    @staticmethod
    @abc.abstractmethod
    def _decrypt(rsa, data):
        pass


class ElectronicCodeBook(BlockCipher):
    @staticmethod
    def encrypt(rsa, data):
        return super(ElectronicCodeBook, ElectronicCodeBook).encrypt(rsa, data, ElectronicCodeBook._encrypt)

    @staticmethod
    def decrypt(rsa, data):
        return super(ElectronicCodeBook, ElectronicCodeBook).decrypt(rsa, data, ElectronicCodeBook._decrypt)

    @staticmethod
    def _encrypt(rsa, byte_array):
        num_zeros = rsa.num_bytes - ElectronicCodeBook.padding_len - len(byte_array)
        zeros = bytearray([0] * num_zeros)
        num_zeros = bytearray(num_zeros.to_bytes(2, byteorder="big"))
        byte_array = num_zeros + zeros + bytearray(byte_array)

        return bytearray(rsa.encrypt(int.from_bytes(byte_array[0: rsa.num_bytes], byteorder="big"))
                         .to_bytes(rsa.num_bytes, "big"))

    @staticmethod
    def _decrypt(rsa, byte_array):
        result = bytearray(rsa.decrypt(int.from_bytes(byte_array[0: rsa.num_bytes], byteorder="big"))
                           .to_bytes(rsa.num_bytes, "big"))

        num_zeros = int.from_bytes(result[ElectronicCodeBook.padding_len - 2:ElectronicCodeBook.padding_len],
                                   byteorder="big")
        return bytearray(result[ElectronicCodeBook.padding_len + num_zeros:])


class Counter(BlockCipher):
    nonce = 123456
    counter = 0

    @staticmethod
    def encrypt(rsa, data):
        Counter.counter = 0
        return super(Counter, Counter).encrypt(rsa, data, Counter._encrypt, padding=False)

    @staticmethod
    def decrypt(rsa, data):
        Counter.counter = 0
        return super(Counter, Counter).decrypt(rsa, data, Counter._decrypt)

    @staticmethod
    def _encrypt(rsa, byte_array):
        enc_non_ctr = bytearray(rsa.encrypt(Counter.nonce + Counter.counter).to_bytes(rsa.num_bytes, "big"))
        Counter.counter += 1
        return bytearray(x ^ y for (x, y) in zip(enc_non_ctr, byte_array))

    @staticmethod
    def _decrypt(rsa, byte_array):
        enc_non_ctr = bytearray(rsa.encrypt(Counter.nonce + Counter.counter).to_bytes(rsa.num_bytes, "big"))
        Counter.counter += 1
        return bytearray(x ^ y for (x, y) in zip(enc_non_ctr, byte_array))


class TestBlockCiphers(unittest.TestCase):
    @staticmethod
    def _encrypt_decrypt(block_cipher, data, rsa=MyRSA(1024, generate_keys=True)):
        enc = block_cipher.encrypt(rsa, bytearray(data))
        dec = block_cipher.decrypt(rsa, enc)
        return dec

    def test_ecb_data_shorter_than_key(self):
        arr = [0, 2, 1, 0, 5]
        self.assertEqual(self._encrypt_decrypt(ElectronicCodeBook, arr), bytearray(arr))

    def test_ecb_data_longer_than_key(self):
        arr = [randint(0, 255) for _ in range(1000)]
        self.assertEqual(self._encrypt_decrypt(ElectronicCodeBook, arr), bytearray(arr))

    def test_ctr_data_shorter_than_key(self):
        arr = [0, 2, 1, 0, 5]
        self.assertEqual(self._encrypt_decrypt(Counter, arr), bytearray(arr))

    def test_ctr_data_longer_than_key(self):
        arr = [randint(0, 255) for _ in range(1000)]
        self.assertEqual(self._encrypt_decrypt(Counter, arr), bytearray(arr))


if __name__ == '__main__':
    unittest.main()



