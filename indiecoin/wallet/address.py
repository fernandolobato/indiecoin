from .. util import ecdsa
from .. util.ecdsa.keys import BadSignatureError


class Address(object):
    """ Class to use eliptic curve asymetric keys.

        This class is a wrapper over pythons implementation of ECDSA.
        Allows us to generate a key pair, load a key from an hexadecimal
        representation or verify a signature given a message, public key
        and signature.

        Reference
        ----------
    """
    def __init__(self, public_key=None, private_key=None):
        """ Constructor method for an indiecoin address.

            Parameters
            ----------
                public_key : str
                    string hexadecimal representation of a public key

                private_key : str
                    string hexadecimal representation of a private key

            Attributes
            -----------

            __private_key : ecdsa.VerifyinKey
                Object representation of private key

            __publick_key : ecdsa.SigningKey
                Object representation of private key

            Notes
            ------
            This function can recieve an hexadecimal representation of a private
            key, turn it into a ecdsa object and generate its corresponding public key.

            If no private or public key are passed. This object generates a new key pair.

            If only public key is passed, this object can't generate signatures, only verify.

        """
        self.__private_key = private_key
        self.__public_key = public_key

        if self.__public_key:
            self.__public_key = ecdsa.VerifyingKey.from_string(
                public_key.decode('hex'),
                curve=ecdsa.NIST521p)

        if self.__private_key:
            self.__private_key = ecdsa.SigningKey.from_string(
                private_key.decode('hex'),
                curve=ecdsa.NIST521p)
            self.__public_key = self.__private_key.get_verifying_key()

        if not self.__private_key and not self.__public_key:
            self.__private_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST521p)
            self.__public_key = self.__private_key.get_verifying_key()

    @property
    def private_key(self):
        """ Function to get the Hexadecimal representation of a ECDSA private key.

            Returns
            -------
            Hexadecimal representation of a private key.
        """
        return self.__private_key.to_string().encode('hex')

    @property
    def public_key(self):
        """ Function to get the Hexadecimal representation of a ECDSA public key.

            Returns
            -------
            Hexadecimal representation of public key.
        """
        return self.__public_key.to_string().encode('hex')

    def sign(self, message):
        """ Signs a message with ecdsa

            Returns
            -------
                hexadecimal representation of signature.

            Raises
            ------
                @TODO: Raise if no private key provided.
        """
        if self.__private_key is not None:
            return self.__private_key.sign_deterministic(message).encode('hex')

        return None

    def verify_signature(self, signature, message):
        """
            Verifies that a signature was made with a specific key pair.

            Catches BadSignatureError if signature is not valid.

            Returns
            -------
                True : Boolean
                    if signature matches public key stored in self.__public_key
                False: Boolean
                    if signature does not match public key stoted in self.__public_key
        """
        try:
            return self.__public_key.verify(signature.decode('hex'), message)
        except BadSignatureError:
            return False
