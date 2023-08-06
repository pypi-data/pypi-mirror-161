import requests
from pathlib import Path

# Used endpoints of DYS
ENDPOINTS = {
    "REPORT": "/OTHER/core/other/htmlreport/"
}


class ZapManager:
    """
     A class to interact with OWASP ZAP API
    Attributes
    ----------
    zap_base_url : str
        OWASP ZAP Endpoint e.g.: "http://localhost:9090"
    zap_api_key: str
        OWASP ZAP token for Authentication & Authorization e.g.: "zaproxy"
    """

    def __init__(self, zap_base_url, zap_api_key):
        if '' not  in zap_base_url:
            raise ValueError("ZAP Base Url cannot be None!")
        if '' not  in zap_api_key:
            raise ValueError("ZAP API Key cannot be None!")
        if zap_base_url[-1] == '/':
            zap_base_url = zap_base_url[:-1]
        self.zap_base_url = zap_base_url
        self.zap_api_key = zap_api_key

    def make_request(self, method: str, url: str, headers=None, **kwargs):
        """
        Requests with basic error handling
        :param method: Request method. Ex: "GET", "POST", "PUT"
        :param url: Request url
        :param headers: (optional) Request headers
        :param kwargs: (optional) Optional parameters of request method. Ex: data, files etc.
        :return: :class:`Response <Response>` object
        """
        if not headers:
            headers = self.HEADERS.copy()
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            return response
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("RequestException:", err)

        return None

    def download_request(self, url: str, filepath: str):
        """
        Downloads File
        :param url: Request url
        :param filepath: File path to download
        :return: :class:`Response <Response>` object
        """
        try:
            response = requests.get(url)
            path = Path(__file__).parent.parent.parent / filepath
            open(path, "wb").write(response.content)
            return response

        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("RequestException:", err)
        return None

    def get_url(self, task: str):
        """
        :param task: task name
        :return: string. Returns the endpoint for a specific task
        :exception: KeyError if task not exist
        """
        return self.zap_base_url + ENDPOINTS[task]

    def get_report(self, filepath: str):
        """
        Gets Zap Report in HTML format and saves to report folder
            :return: response code
        """
        url = self.get_url("REPORT") + "?apikey=" + self.zap_api_key
        res = self.download_request(url, filepath)
        return res.status_code
