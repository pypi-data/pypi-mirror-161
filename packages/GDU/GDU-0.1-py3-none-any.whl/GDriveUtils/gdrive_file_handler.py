from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from pydrive2.files import GoogleDriveFile
from oauth2client.service_account import ServiceAccountCredentials

from .config import default_permission


class GdriveFileHandler(object):

    # https://docs.iterative.ai/PyDrive2/filemanagement/

    def __init__(self, *args, **kwargs):

        self._gauth = None
        self._drive = None

        self.keyfile = kwargs.get('keyfile')
        self.gauth = kwargs.get('gauth', None)
        self.drive = kwargs.get('drive', None)

    @property
    def gauth(self):
        if self._gauth is None:
            scope = ["https://www.googleapis.com/auth/drive"]
            self._gauth = GoogleAuth()
            self._gauth.auth_method = 'service'
            self._gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.keyfile, scope)
        return self._gauth

    @gauth.setter
    def gauth(self, value):
        self._gauth = value

    @property
    def drive(self):
        if self._drive is None:
            self._drive = GoogleDrive(self.gauth)
        return self._drive

    @drive.setter
    def drive(self, value):
        self._drive = value

    def create_file(self, title, mimetype=None, content: str = None, parent=None, permission=None):
        """

        :param title:
        :param mimetype: https://developers.google.com/drive/api/guides/mime-types
        :param content:
        :param parents:
        """
        metadata = {'title': title}
        if mimetype is not None:
            metadata['mimetype'] = mimetype

        if parent is not None:
            if isinstance(parent, GoogleDriveFile):
                metadata['parents'] = [{'id': parent['id']}]
            elif isinstance(parent, str):
                metadata['parents'] = [{'id': parent}]
            else:
                raise ValueError('Parent must be a GoogleDriveFile or str')

        file = self.drive.CreateFile(metadata)

        if content is not None:
            file.SetContentString(content)

        file.Upload(param={'supportsTeamDrives': True})

        if permission is None:
            permission = default_permission

        _ = file.auth.service.permissions().insert(
            fileId=file['id'], body=permission, supportsTeamDrives=True).execute(http=file.http)
        file.Upload()
        print(file['alternateLink'])

        return file

    def create_folder(self, folder_name, parent=None, permission=None):
        metadata = {
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if parent is not None:
            if isinstance(parent, GoogleDriveFile):
                metadata['parents'] = [{'id': parent['id']}]
            elif isinstance(parent, str):
                metadata['parents'] = [{'id': parent}]
            else:
                raise ValueError('Parent must be a GoogleDriveFile or str')

        folder = self.drive.CreateFile(metadata)
        folder.Upload()

        if permission is None:
            permission = default_permission

        _ = folder.auth.service.permissions().insert(
            fileId=folder['id'], body=permission, supportsTeamDrives=True).execute(http=folder.http)

        return folder

    def get_file_by_id(self, file_id):
        return self.drive.CreateFile({'id': file_id})

    def list_files(self, parent=None):

        if parent is not None:
            if isinstance(parent, GoogleDriveFile):
                folder_id = [{'id': parent['id']}]
            elif isinstance(parent, str):
                folder_id = [{'id': parent}]
            else:
                raise ValueError('Parent must be a GoogleDriveFile or str')
        else:
            folder_id = 'root'

        return self.drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
