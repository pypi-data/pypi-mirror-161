"""
XNAT DATA EXPLORER
"""

from ..core.sess import XNATSession
from typing import List, Union


class XNATExplorer(object):
    """
    Provides Basic Queries into the XNAT database
    """

    def __init__(self, xnat: XNATSession):
        """
        :param xnat: XNAT BASE SESSION
        """
        # needs xnat session to operate
        self.xnat = xnat
        # map the xnat session into session for interpretable functions
        self.session = self.xnat.session

    # need more get all methods for scans and data
    def get_all_projects(self) -> List[str]:
        """
        Gets all the project names, could be resource heavy
        :return: List of all project names
        """
        # select interface gives filtering
        # get all projects
        # not optimal on central
        return list(self.session.select.projects())

    def get_all_subjects(self) -> List[str]:
        """
        Gets all the subject names, could be resource heavy
        :return: List of all subject names
        """
        # select interface gives filtering
        # get all projects
        # not optimal on central
        return list(self.session.select.projects().subjects())

    def get_all_experiments(self) -> List[str]:
        """
        Gets all the experiment names, could be resource heavy
        :return: List of all subject names
        """
        # select interface gives filtering
        # get all projects
        # not optimal on central
        return list(self.session.select.projects().subjects().experiments())

    def get_all_scans(self) -> List[str]:
        """
        Gets all the scan names, could be resource heavy
        :return: List of all subject names
        """
        # select interface gives filtering
        # get all projects
        # not optimal on central
        return list(self.session.select.projects().subjects().experiments().scans())

    # specific methods

    def get_project(self, proj_id: Union[int, str]):
        """
        :param proj_id: project id or name to be requested
        :return: project object to be operated on
        """
        # example 123456898 in central
        return self.session.select(f'/project/{proj_id}')

    def get_subject(self, proj_id: str, subj_id: str):
        """
        :param proj_id: project id or name to be requested
        :param subj_id: subject id or name to be requested
        :return: subject object to be operated on
        """
        # example CENTRAL04_S01706 in central
        return self.session.select(f'/project/{proj_id}/subject/{subj_id}')

    def get_experiment(self, proj_id: str, subj_id: str, exp_id: str):
        """
        :param proj_id: project id to be requested
        :param subj_id: subject id or name to be requested
        :param exp_id: experiment id or name to be requested
        :return: experiment object to be operated on
        """
        # example CENTRAL04_E03123 in central
        return self.session.select(f'/project/{proj_id}/subject/{subj_id}/experiment/{exp_id}')

    def get_scan(self, proj_id: str, subj_id: str, exp_id: str, scan_id: str):
        """
        :param proj_id: project id or name to be requested
        :param subj_id: subject id or name to be requested
        :param exp_id: experiment id or name to be requested
        :param scan_id: scan id or name to be requested
        :return: scan object to be operated on
        """
        # example 2 in central
        return self.session.select(f'/project/{proj_id}/subject/{subj_id}/experiment/{exp_id}/scan/{scan_id}')

    def get_xnat_url(self, url: str):
        """
        Custom Queries, can be really helpful if u have something specific in mind that is not provided
        basically lets u call xnat as intended if u have an understanding of the data structure
        URL SCHEMA
        /project/{proj_id}/subject/{subj_id}/experiment/{exp_id}/scan/{scan_id}
        :param url: xnat url to get
        :return: list of the available options, Can be objects, or list of names, or even files
        """
        return self.session.select(url)
