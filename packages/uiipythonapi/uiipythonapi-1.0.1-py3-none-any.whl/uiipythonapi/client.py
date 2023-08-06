"""
Client implementation for the Virtomize UII API.
"""
# pylint: disable=too-many-arguments,broad-except
import requests

BASE_URL = "https://api.virtomize.com/uii/"


class Client:
    """ Client to interact with the Virtomize UII API. """
    def __init__(self, token):
        self.token = token

    def read_os_list(self):
        """ Read a list of all supported operating systems """
        endpoint = BASE_URL + "oslist"
        headers = self.__default_header()

        response = requests.get(endpoint, headers=headers, verify=False)
        if not response.status_code == 200:
            return [], parse_error(response)

        response_json = response.json()
        if "_embedded" in response_json:
            return response_json["_embedded"], None

        return [], "no data returned"

    def read_package_list(self, dist: str, version: str, arch: str):
        """ Read a list of all available packages for an operating system """
        endpoint = BASE_URL + "packages"
        headers = self.__default_header()
        data = {
            "arch": arch,
            "dist": dist,
            "version": version,
        }

        response = requests.post(endpoint, data=data, headers=headers, verify=False)
        if not response.status_code == 200:
            return [], parse_error(response)

        response_json = response.json()
        if "_embedded" in response_json:
            if "packages" in response_json["_embedded"]:
                return response_json["_embedded"]["packages"], None

        return [], "no data returned"

    def build(self,
              destination: str,
              dist: str,
              version: str,
              arch: str,
              hostname: str,
              networks) -> str:
        """ Build an ISO """
        endpoint = BASE_URL + "images"
        headers = self.__default_header()
        data = {
            "arch": arch,
            "dist": dist,
            "version": version,
            "hostname": hostname,
            "networks": networks
        }

        response = requests.post(endpoint, json=data, headers=headers, verify=False)
        if not response.status_code == 200:
            return parse_error(response)

        with open(destination, "wb") as iso_file:
            for chunk in response.iter_content(chunk_size=16 * 1024):
                iso_file.write(chunk)
        return ""

    def __default_header(self):
        return {
            "Authorization": "Bearer " + self.token,
            "User-Agen": "UII-Python-API-1.0.1"
        }

def parse_error(response) -> str:
    """ Parse an error returned by the API """
    try:
        response_json = response.json()
        if "errors" in response_json:
            errors = response_json["errors"]
            return ", ".join(errors)
    except Exception as ex:
        print(f'Error calling API: {ex}')

    return "request was not successful and returned \"" + str(response.content) + "\""
