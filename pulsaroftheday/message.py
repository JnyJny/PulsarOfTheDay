"""
"""

from .catalog import Pulsar


class Message:
    def __init__(self, pulsar: Pulsar = None) -> None:
        self.pulsar = pulsar
