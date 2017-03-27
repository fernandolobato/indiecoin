#!/usr/bin/env python
import argparse

from indiecoin.node import IndieCoinNode
from indiecoin.miner import Miner


def main():
    """
    """
    parser = argparse.ArgumentParser(description="Indiecoin Tool")

    mining_group = parser.add_argument_group(title="Mining")
    mining_group.add_argument(
        '--mine',
        default=False,
        metavar="MINE",
        help="Run the node as a miner node.")

    peer_group = parser.add_argument_group(title="Peer Discovery")
    peer_group.add_argument(
        '--initial-peers',
        default=None,
        metavar="INITIAL_PEER",
        help="Connect to a know peer on bootstrap")

    peer_group.add_argument(
        '--max-peers',
        metavar="MAX_PEERS",
        type=int, default=50,
        help="maximum connections to allow (default: 50)")

    network_group = parser.add_argument_group(title="Network")

    network_group.add_argument(
        '--bind',
        metavar="ADDRESS",
        default="0.0.0.0",
        help="Use specific interface (default: 0.0.0.0)")

    network_group.add_argument(
        '--port',
        default=6666,
        type=int,
        help="port to connect on (default: 6666)")

    args = parser.parse_args()

    if args.mine:
        miner = Miner()
        miner.start()

    node = IndieCoinNode(args.max_peers, args.port)

    if args.initial_peers:
        for peer in args.initial_peers.split(','):
            host, port = peer.split(':')
            node.addpeer(peer, host, port)

    node.start()
    node.bootstrap()


if __name__ == '__main__':
    main()
