# -*- coding: utf-8 -*-
import unittest

from context import indiecoin
from indiecoin.wallet.address import Address
from indiecoin.util import hash


class AddressTestCase(unittest.TestCase):
    """ Test the functionality for generating ECDSA key pairs.
    """
    def setUp(self):
        self.base_address = Address()

    def test_generating_key_pair(self):
        """ Test a new key pair can be generated
        """
        address = Address()

        self.assertEqual(len(address.public_key), 264)
        self.assertEqual(len(address.private_key), 132)

    def test_reloading_private_key(self):
        """ Test an address object can be created recieving
            a private key in string hexadecimal representation
            as parameter.
        """

        private_key = self.base_address.private_key
        public_key = self.base_address.public_key

        address = Address(private_key=private_key)
        self.assertEqual(address.private_key, private_key)
        self.assertEqual(address.public_key, public_key)

    def test_signature_hash(self):
        """ Test that a message hashed can be signed and verified
        """
        message = hash.sha256('Value does not exist outside concioussnes of men')
        signature = self.base_address.sign(message)

        self.assertTrue(self.base_address.verify_signature(signature, message))

    def test_incorrect_signature(self):
        """ Test that an incorrect message signature is not verified
        """
        message = hash.sha256('Value does not exist outside concioussnes of men')
        signature = self.base_address.sign(message)
        message += 'Empty Space'

        self.assertFalse(self.base_address.verify_signature(signature, message))

    def test_verify_from_public_key(self):
        """ Tests an address can be instantiated with a public key 
            and verify a message with that key.
        """
        message = hash.sha256('Value does not exist outside concioussnes of men')
        signature = self.base_address.sign(message)

        address = Address(public_key=self.base_address.public_key)

        self.assertTrue(address.verify_signature(signature, message))

    def test_no_signature_without_private_key(self):
        """ Test an address can not sign withou a private key.
        """
        message = hash.sha256('Value does not exist outside concioussnes of men')
        address = Address(public_key=self.base_address.public_key)

        self.assertEqual(address.sign(message), None)

if __name__ == '__main__':
    unittest.main()