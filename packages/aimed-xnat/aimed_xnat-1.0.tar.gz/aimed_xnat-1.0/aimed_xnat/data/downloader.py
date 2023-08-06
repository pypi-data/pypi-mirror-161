"""
XNAT DOWNLOADER
"""

from ..core.sess import XNATSession
from ..data.explorer import XNATExplorer
import os


class XNATDownloader(object):
    """
    Allows Downloading from each level of the XNAT schema using custom types
    """

    def __init__(self, xnat: XNATSession):
        """
        :param xnat: XNAT BASE SESSION
        """
        # needs xnat session to operate
        self.xnat = xnat
        # map the xnat session into session for for interpretable functions
        self.session = self.xnat.session
        self.explorer = XNATExplorer(xnat=xnat)

    def download(self, output_directory: str, level: str, resource_type: str,
                 proj_id=None, subj_id=None, exp_id=None, scan_id=None,
                 log=False, file_name=None) -> bool:
        """
        Downloader Func
        :param output_directory: directory to save the files in.
        :param level: upload place from [project, subject, experiment, scan]
        :param resource_type: type of the file being upload for ex TXT.
        :param proj_id: project id or name to be requested
        :param subj_id: subject id or name to be requested
        :param exp_id: experiment id or name to be requested
        :param scan_id: subject id or name to be requested
        :param log: whatever to log at each level or not.
        :param file_name: filename if only one file is required not the whole directory of dicoms for example.
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
        # check to see if it's a dir or a file
        resource_object = query.resource(resource_type)
        if log:
            print(f'[INFO] resource type: {resource_type}')
        files = resource_object.files().get()
        no_files = len(list(resource_object.files()))
        if no_files == 0:
            status = False
            print(f"[Warning] Nothing to Download!")
            return status
        # check filename
        if file_name is not None:
            if file_name not in files:
                status = False
                print(f"[WARNING] File Does Not Exist")
                return status
            # so the file is there
            else:
                # download the file only then
                if os.path.isdir(output_directory):
                    for filename in files:
                        if filename == file_name:
                            resource_object.file(filename).get_copy(os.path.join(output_directory, filename))
                else:
                    os.makedirs(output_directory)
                    for filename in files:
                        if filename == file_name:
                            resource_object.file(filename).get_copy(os.path.join(output_directory, filename))
                status = True
        else:
            # download all
            if os.path.isdir(output_directory):
                for filename in files:
                    resource_object.file(filename).get_copy(os.path.join(output_directory, filename))
            else:
                os.makedirs(output_directory)
                for filename in files:
                    resource_object.file(filename).get_copy(os.path.join(output_directory, filename))
            status = True
        return status

    # TODO: add creations