import bt_peer

from protocol import protocol


class IndieCoinPeer(bt_peer.BTPeer):
    """ Implements a file-sharing peer-to-peer entity based on the generic
    BerryTella P2P framework.
    """

    def __init__(self, maxpeers, serverport, miner=None, check_on_miner=None):
        """ Initializes the peer to support connections up to maxpeers number
        of peers, with its server listening on the specified port.

        """
        bt_peer.BTPeer.__init__(
            self,
            maxpeers,
            serverport,
            miner=miner,
            check_on_miner=check_on_miner)

        self.addrouter(self.__router)

        handlers = {
                protocol.LISTPEERS: self.__handle_listpeers,
                protocol.INSERTPEER: self.__handle_insertpeer,
                protocol.PEERNAME: self.__handle_peername,
                protocol.PEERQUIT: self.__handle_quit}

        for mt in handlers:
            self.addhandler(mt, handlers[mt])

    def __debug(self, msg):
        if self.debug:
            bt_peer.btdebug(msg)

    def __router(self, peerid):
        if peerid not in self.get_peer_ids():
            return (None, None, None)
        else:
            rt = [peerid]
            rt.extend(self.peers[peerid])
            return rt

    def __handle_insertpeer(self, peerconn, data):
        """ Handles the INSERTPEER (join) message type. The message data
        should be a string of the form, "peerid  host  port", where peer-id
        is the canonical name of the peer that desires to be added to this
        peer's list of peers, host and port are the necessary data to connect
        to the peer.
        """
        self.peerlock.acquire()
        try:
            try:
                peerid, host, port = data.split()

                if self.maxpeersreached():
                    self.__debug(
                        'maxpeers %d reached: connection terminating' % self.maxpeers)
                    peerconn.send_data(protocol.ERROR, 'Join: too many peers')
                    return

                if peerid not in self.get_peer_ids() and peerid != self.myid:
                    self.addpeer(peerid, host, port)
                    self.__debug('added peer: %s' % peerid)
                    peerconn.send_data(protocol.REPLY, 'Join: peer added: %s' % peerid)
                else:
                    peerconn.send_data(
                        protocol.ERROR,
                        'Join: peer already inserted %s' % peerid)
            except:
                self.__debug('invalid insert %s: %s' % (str(peerconn), data))
                peerconn.send_data(protocol.ERROR, 'Join: incorrect arguments')
        finally:
            self.peerlock.release()

    def __handle_listpeers(self, peerconn, data):
        """ Handles the LISTPEERS message type. Message data is not used.
        """
        self.peerlock.acquire()
        try:
            self.__debug('Listing peers %d' % self.number_of_peers())
            peerconn.send_data(protocol.REPLY, '%d' % self.number_of_peers())
            for pid in self.get_peer_ids():
                host, port = self.get_peer(pid)
                peerconn.send_data(protocol.REPLY, '%s %s %d' % (pid, host, port))
        finally:
            self.peerlock.release()

    def __handle_peername(self, peerconn, data):
        """ Handles the NAME message type. Message data is not used.
        """
        peerconn.send_data(protocol.REPLY, self.myid)

    def __handle_quit(self, peerconn, data):
        """ Handles the QUIT message type. The message data should be in the
        format of a string, "peer-id", where peer-id is the canonical
        name of the peer that wishes to be unregistered from this
        peer's directory.

        """
        self.peerlock.acquire()
        try:
            peerid = data.lstrip().rstrip()
            if peerid in self.get_peer_ids():
                msg = 'Quit: peer removed: %s' % peerid
                self.__debug(msg)
                peerconn.send_data(protocol.REPLY, msg)
                self.removepeer(peerid)
            else:
                msg = 'Quit: peer not found: %s' % peerid
                self.__debug(msg)
                peerconn.send_data(protocol.ERROR, msg)
        finally:
            self.peerlock.release()

    # def buildpeers(self, host, port, hops=1):
    #     """ buildpeers(host, port, hops)

    #     Attempt to build the local peer list up to the limit stored by
    #     self.maxpeers, using a simple depth-first search given an
    #     initial host and port as starting point. The depth of the
    #     search is limited by the hops parameter.

    #     """
    #     if self.maxpeersreached() or not hops:
    #         return

    #     peerid = None

    #     self.__debug("Building peers from (%s,%s)" % (host,port))

    #     try:
    #         _, peerid = self.connectandsend(host, port, PEERNAME, '')[0]

    #         self.__debug("contacted " + peerid)

    #         resp = self.connectandsend(host, port, INSERTPEER,
    #                     '%s %s %d' % (self.myid,
    #                               self.serverhost,
    #                               self.serverport))[0]
    #         self.__debug(str(resp))

    #         if (resp[0] != REPLY) or (peerid in self.get_peer_ids()):
    #             print(resp[1])
    #             return

    #         self.addpeer(peerid, host, port)

    #         # do recursive depth first search to add more peers
    #         resp = self.connectandsend(host, port, LISTPEERS, '',
    #                     pid=peerid)

    #         if len(resp.data) > 1:

    #             while len(resp):
    #                 nextpid,host,port = resp.pop()[1].split()
    #                 if nextpid != self.myid:
    #                     self.buildpeers(host, port, hops - 1)
    #     except:
    #         if self.debug:
    #             traceback.print_exc()
    #             self.removepeer(peerid)
