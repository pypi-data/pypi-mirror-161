from os import stat
import requests

from .helpers import convert_list_to_dict, convert_list_to_string


class Wrike:
    """
    A wrapper for Wrike API calls. Some API calls save data to a cache which this object manages. If at some point you'd like to clear those caches, simply call wrike.reinitialize()

    Args:
        :param base_url (string): Base Wrike URL, it should look like "https://<host>/api/v4/" (the trailing / is important)
        :param perm_access_token (string): A permanent access token obtained from Wrike's dashboard
        :param ssl_verify (bool): Set to false during testing

    """

    def __init__(self, base_url: str, perm_access_token: str, ssl_verify: bool = True):
        self.base_url = base_url
        self.ssl_verify = ssl_verify
        self.__headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + perm_access_token,
        }
        self.reinitialize()

    def reinitialize(self):
        """
        Clears the wrike's object data cache
        """
        self._contacts = None
        self._custom_fields = None
        self._custom_statuses = None
        self._folders = None
        self._workflows = None

    # region Properties (Does Caching)

    @property
    def contacts(self) -> dict:
        if not self._contacts:
            all_contacts = self.query_contacts_all()["data"]
            self._contacts = convert_list_to_dict(all_contacts)
        return self._contacts

    @property
    def custom_fields(self) -> dict:
        if not self._custom_fields:
            all_custom_fields = self.query_custom_fields_all()["data"]
            self._custom_fields = convert_list_to_dict(all_custom_fields)
        return self._custom_fields

    @property
    def custom_statuses(self) -> dict:
        if not self._custom_statuses:
            self._custom_statuses = {}
            for workflow in self.workflows.values():
                for custom_status in workflow["customStatuses"]:
                    self._custom_statuses[custom_status["id"]] = custom_status
        return self._custom_statuses

    @property
    def folders(self) -> dict:
        if not self._folders:
            all_folders = self.query_folders_all()["data"]
            self._folders = convert_list_to_dict(all_folders)
        return self._folders

    @property
    def workflows(self) -> dict:
        if not self._workflows:
            workflows = self.query_workflows()["data"]
            self._workflows = convert_list_to_dict(workflows)
        return self._workflows

    # endregion

    # region Base HTTP Methods

    def get(self, path: str) -> dict:
        response = requests.get(
            self.base_url + path, headers=self.__headers, verify=self.ssl_verify
        )
        return response.json()

    def post(self, path: str, body: dict) -> dict:
        response = requests.post(
            self.base_url + path,
            json=body,
            headers=self.__headers,
            verify=self.ssl_verify,
        )
        return response.json()

    # endregion

    # region Contacts

    def query_contacts(self, ids: list) -> dict:
        ids = convert_list_to_string(ids)
        return self.get(f"contacts/{ids}")

    def query_contacts_all(self) -> dict:
        return self.get("contacts")

    def query_contact_me(self) -> dict:
        return self.get("contacts?me=true")

    # endregion

    # region Custom Fields

    def query_custom_fields(self, ids: list) -> dict:
        ids = convert_list_to_string(ids)
        return self.get(f"customfields/{ids}")

    def query_custom_fields_all(self) -> dict:
        return self.get("customfields")

    # endregion

    # region Extract Methods

    def extract_project_status(self, folder: dict) -> str:
        """
        Extracts project status from a folder. Returns None if it isn't set
        """
        # return "test"
        status = Wrike.extract_value_from_project("status", folder)
        custom_status_id = Wrike.extract_value_from_project("customStatusId", folder)
        if str(status) == "Custom" and custom_status_id:
            status = self.custom_statuses[custom_status_id]["name"]

        return status

    @staticmethod
    def extract_value_from_project(key: str, folder: dict):
        """
        Returns the value at specified key in a folder's 'project' object.
        If the key doesn't exist, returns None
        """
        try:
            extract = folder["project"][key]
            return extract
        except Exception as e:
            return None

    # endregion

    # region Folders

    def query_folders(self, ids: list) -> dict:
        ids = convert_list_to_string(ids)
        return self.get(f"folders/{ids}")

    def query_folders_all(self) -> dict:
        return self.get("folders")

    def query_folder_by_title(self, title: str) -> dict:
        for key, folder in self.folders.items():
            if folder["title"] == title:
                return folder

    def query_folder_subtrees(self, folder_id: str) -> dict:
        return self.get(f"folders/{folder_id}/folders")

    def query_folder_subtrees_by_title(self, title: str) -> dict:
        folder = self.query_folder_by_title(title)
        return self.query_folder_subtrees(folder["id"])

    # endregion

    # region Groups

    def query_group(self, group_id: str) -> dict:
        return self.get(f"groups/{group_id}")

    def query_groups_all(self) -> dict:
        return self.get(f"groups")

    # endregion

    # region Tasks

    def query_tasks(self, ids: list) -> dict:
        ids = convert_list_to_string(ids)
        return self.get(f"tasks/{ids}")

    def query_tasks_all(self) -> dict:
        return self.get("tasks")

    def query_tasks_in_folder(self, folder_id: str) -> dict:
        return self.get(f"folders/{folder_id}/tasks")

    # endregion

    # region Users

    def query_user(self, user_id: str) -> dict:
        return self.get(f"users/{user_id}")

    # endregion

    # region Workflows

    def query_workflows(self) -> dict:
        return self.get("workflows")

    # endregion
