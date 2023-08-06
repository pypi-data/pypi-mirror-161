"""
XNAT UTILITIES
"""

from ..core.sess import XNATSession


class XNATUtil(object):
    """
    Provides Basic Features of the XNAT db provided by pyxnat
    """
    def __init__(self, xnat: XNATSession):
        """
        :param xnat: XNAT BASE SESSION
        """
        # needs xnat session to operate
        self.xnat = xnat
        # map the xnat session into session for interpretable functions
        self.session = self.xnat.session

    def print_struct(self) -> None:
        """
        Prints the XNAT file structure
        :return: None
        """
        self.session.inspect.structure()

    def save_cfg(self) -> None:
        """
        Save the login cfg.
        :return: None
        """
        # can save the session config
        # ofc login has to come from UI that way
        self.session.save_config('./user.cfg')
