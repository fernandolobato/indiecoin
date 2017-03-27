import json

import protocol


class Response(object):
    """ Response object for all incoming communication between
        indiecoin nodes.

        This class serves as a wrapper for the generic BerryTella
        P2P framework communication.

        Attributes
        ----------
        __response_type: constant from node.protocol.protocol
            constant indicating type of response
        __data: string
            information sent over network.

    """
    def __init__(self, response_type, data):
        """
        """
        self.__response_type = response_type
        self.__data = data

    @property
    def text(self):
        """ Returns text representation of data exchanged in request.
        """
        return str(self.__data)

    @property
    def code(self):
        """ Returns the response typ
        """
        return self.__response_type

    @property
    def data(self):
        """ Dictionary representation of test information.

            Before sending block or transactions in request,
            they are serialized and turne to json strings.
            Everything we get is a JSON string which must be
            re-serialized to a dictionary.

            Returns
            -------
                data: dictionary
                    dictionary representation of information.
        """
        data = json.loads(self.text)
        return data

    def is_successful(self):
        """ Allows to verify if there has been an error in the response.

            Returns
            -------
                False if response type is protocol.Error,
                Truth otherwise.
        """
        if self.__response_type == protocol.ERROR:
            return False
        return True

    def __str__(self):
        return 'response: {}'.format(self.code)
