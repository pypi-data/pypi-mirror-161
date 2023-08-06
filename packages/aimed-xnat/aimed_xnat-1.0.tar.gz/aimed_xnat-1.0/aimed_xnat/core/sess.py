"""
XNAT BASE SESSION
"""

from pyxnat import Interface
import pyxnat


class XNATSession(object):
    """
    Basic XNAT Authentication and Database Access.
    """

    def __init__(self, server: str,
                 user: str,
                 password: str) -> None:
        """
        Constructor
        :param server: XNAT server address
        :param user: login username
        :param password: login password
        """
        self.session: pyxnat.Interface = Interface(server=server,
                                                   user=user,
                                                   password=password)

    def __del__(self) -> None:
        """
        Try to close the XNAT Jsession on delete if not already closed.
        its always closed though.
        :return: None
        """
        try:
            self.session.close_jsession()
        except Exception as e:
            print(f'[DEBUG] error on closing connection: {e}')
