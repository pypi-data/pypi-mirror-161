import os
import logging
import requests
import ldap3
from wikijspy import *

logger = logging.getLogger(__name__)

class ApiExtensions:
    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client
        self.file_ext_dict = None

    def upload_asset(self, file_path: str, folderId: int = 0):
        if not self.file_ext_dict:
            self.file_ext_dict = {
                ".png" : "image/png",
                ".jpg" : "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif" : "image/gif",
                ".pdf" : "application/pdf",
                ".log" : "text/x-log",
                ".bin" : "application/octet-stream",
                ".txt" : "text/plain",
                ".zip" : "application/zip",
                ".diff": "text/x-patch",
                ".ico" : "image/x-icon"
            }
        
        url = f'{self.api_client.hostname}/u'
        
        headers = {
            'Authorization': f'Bearer {self.api_client.token}'
        }
        
        with open(file_path, 'rb') as f:
            files = (
                ('mediaUpload', (None, '{"folderId":'f'{folderId}''}')),
                ('mediaUpload', (os.path.basename(file_path), f.read(), self.file_ext_dict.get(os.path.splitext(file_path)[1], 'text/plain')))
            )

        return requests.post(url, headers=headers, files=files)


    def import_users_from_ldap(self, ldap_host: str, admin_dn: str, admin_passwd: str, ldap_search_dn: str, ldap_filter: str):
        users_api = UsersApi(self.api_client)
        ldap = ldap3.Server(ldap_host)
        ldap_connection = ldap3.Connection(ldap, admin_dn, admin_passwd)
        ldap_connection.bind()
        
        ldap_connection.search(ldap_search_dn, ldap_filter, attributes=['cn', 'mail', 'userPassword'])
        
        strats = self.api_client.send_request("query{authentication{activeStrategies(enabledOnly: true){displayName,key,strategy{key}}}}")
        
        ldap_strat_key = None
        
        for strat in strats["authentication"]["activeStrategies"]:
            if strat["strategy"]["key"] == "ldap":
                logger.info(f"Using Strategy {strat['displayName']}")
                ldap_strat_key = strat["key"]
        
        if ldap_strat_key is None:
            logger.error("Couldn't find a valid Authentication Strategy!")
            return

        for entry in ldap_connection.entries:
            logger.info(f"Creating user {str(entry['cn'])}.")
            result = users_api.create(UserResponseOutput({"responseResult": ["errorCode", "message"]}), str(entry["mail"]), str(entry["cn"]), ldap_strat_key, str(entry["userPassword"]))
            error_code = result["users"]["create"]["responseResult"]["errorCode"]
            if error_code == AuthenticationUserErrors.AuthAccountAlreadyExists:
                logger.warning(f"There already is an account using this email: {str(entry['mail'])}")
            if error_code == AuthenticationUserErrors.InputInvalid:
                logger.warning(f"The email of the LDAP user {str(entry['cn'])} is invalid!")
    
    def rerender_all_pages(self):
        pages_api = PagesApi(self.api_client)
        
        page_list = [(id["id"], id["path"]) for id in pages_api.list(PageListItemOutput(["id", "path"]))["pages"]["list"]]
        
        for id,path in page_list:
            pages_api.render(DefaultResponseOutput({"responseResult": ["errorCode"]}), id)
            logger.info(f"Rerendered {path}")
    
    def delete_all_pages(self):
        pages_api = PagesApi(self.api_client)
        
        page_list = [(id["id"], id["path"]) for id in pages_api.list(PageListItemOutput(["id", "path"]))["pages"]["list"]]
        
        for id,path in page_list:
            pages_api.delete(DefaultResponseOutput({"responseResult": ["errorCode"]}), id)
            logger.info(f"Deleted {path}")
        
        

