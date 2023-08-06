"""
XNAT Uploader
"""

from ..core.sess import XNATSession
from ..data.explorer import XNATExplorer
import os


class XNATUploader(object):
    """
    Allows Uploading into each level of the XNAT schema using custom types
    """

    def __init__(self, xnat: XNATSession):
        """
        :param xnat: XNAT BASE SESSION
        """
        # needs xnat session to operate
        self.xnat = xnat
        # map the xnat session into session for interpretable functions
        self.session = self.xnat.session
        self.explorer = XNATExplorer(xnat=xnat)

    def upload(self, filepath: str, output_name: str, level: str, resource_type: str,
               proj_id=None, subj_id=None, exp_id=None, scan_id=None,
               log=False, overwrite=True) -> bool:
        """
        Uploader Func
        :param filepath: path to the file on local system
        :param output_name: output file name on xnat
        :param level: upload place from [project, subject, experiment, scan]
        :param resource_type: type of the file being upload for ex TXT.
        :param proj_id: project id or name to be requested
        :param subj_id: subject id or name to be requested
        :param exp_id: experiment id or name to be requested
        :param scan_id: subject id or name to be requested
        :param log: whatever to log at each level or not.
        :param overwrite: whatever to overwrite an existing file
        :return: Upload Status as a boolean
        """
        resource_type = resource_type.upper()
        accepted_levels = ['project', 'subject', 'experiment', 'scan']
        if level not in accepted_levels:
            raise ValueError(f"level must be in {accepted_levels}.")
        elif level == 'project':
            assert proj_id is not None, "must provide proj_id for project level"
            query = self.explorer.get_xnat_url(f'/project/{proj_id}')
            if log:
                print(f'[INFO] project level selected.\n{query}')
        elif level == 'subject':
            assert proj_id is not None, "must provide proj_id for subject level"
            assert subj_id is not None, "must provide subj_id for subject level"
            query = self.explorer.get_xnat_url(f'/project/{proj_id}/subject/{subj_id}')
            if log:
                print(f'[INFO] subject level selected.\n{query}')
        elif level == 'experiment':
            assert proj_id is not None, "must provide proj_id for experiment level"
            assert subj_id is not None, "must provide subj_id for experiment level"
            assert exp_id is not None, "must provide exp_id for experiment level"
            query = self.explorer.get_xnat_url(f'/project/{proj_id}/subject/{subj_id}/experiment/{exp_id}')
            if log:
                print(f'[INFO] project experiment selected.\n{query}')
        else:
            assert proj_id is not None, "must provide proj_id for scan level"
            assert subj_id is not None, "must provide subj_id for scan level"
            assert exp_id is not None, "must provide exp_id for scan level"
            assert scan_id is not None, "must provide scan_id for scan level"
            query = self.explorer.get_xnat_url(f'/project/{proj_id}/subject/{subj_id}/experiment/{exp_id}/scan/{scan_id}')
            if log:
                print(f'[INFO] project scan selected.\n{query}')
        # passed input tests then try to upload
        # check to see if its a dir or a file
        resource_object = query.resource(resource_type)
        if log:
            print(f'[INFO] resource type: {resource_type}')
        try:
            if os.path.isdir(filepath):
                # upload the whole dir
                resource_object.put_dir(filepath)
                status = True
                message = f"[INFO] directory: {filepath}, with datatype: {resource_type} was uploaded at {level} level."
                print(message)
            else:
                # upload the file
                resource_object.file(output_name).insert(src=filepath, overwrite=overwrite)
                status = True
                message = f"[INFO] file: {filepath}, with datatype: {resource_type} was uploaded at {level} level."
                print(message)
        except Exception as e:
            print(f'[WARNING] problems uploading...\n{e}')
            status = False
        return status

    # TODO: add creations
