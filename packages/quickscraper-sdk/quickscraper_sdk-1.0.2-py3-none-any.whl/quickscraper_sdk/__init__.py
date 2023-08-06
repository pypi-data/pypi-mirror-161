"""
quickscraper-sdk
~~~~~~
The quickscraper-sdk package - a Python package template project that is intended
to be used as a cookie-cutter for developing new Python packages.
"""

from .constant import BASE_URL, VERSION
from urllib.parse import urlencode
from base64 import b64decode
import requests


class QuickScraper:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.parse_url = BASE_URL + 'parse'

    def getHtml(self, url: str,
                render: bool = None,
                session_number: str = None,
                country_code: str = None,
                premium: bool = None,
                keep_headers: bool = None,
                headers: dict = {},
                format: str = 'html'):
        request_url = self.__prepareRequestUrl(
            url=url, render=render, session_number=session_number, country_code=country_code,
            premium=premium, keep_headers=keep_headers, format=format)
        custom_headers = headers
        request_options = self.__prepareHeaders(custom_headers, keep_headers)
        response = requests.get(request_url, headers=request_options)
        try:
            body_json = response.json()
            response._content = bytes(body_json['message'], 'utf-8')
        except:
            pass
        return response

    def writeHtmlToFile(self, url: str, file_path: str, render: bool = None,
                        session_number: str = None, country_code: str = None,
                        premium: bool = None, keep_headers: bool = None,
                        headers: dict = {}, format: str = None):
        with open(file_path, 'wb') as file:
            response = self.getHtml(
                url, render, session_number, country_code, premium, keep_headers, headers, format)
            if format == 'images' or format == 'docx':
                try:
                    response._content = b64decode(response.text)
                except:
                    pass
            file.write(response.content)
        return response

    # def writeCSVFile(self, url: str, file_path: str, render: bool = None,
    #                  session_number: str = None, country_code: str = None,
    #                  premium: bool = None, keep_headers: bool = None,
    #                  headers: dict = {}):
    #     response = self.writeHtmlToFile(url, file_path, render, session_number, country_code,
    #                                     premium, keep_headers, headers, format='tables')
    #     return response

    # def getAllImagesInZip(self, url: str, file_path: str, render: bool = None,
    #                       session_number: str = None, country_code: str = None,
    #                       premium: bool = None, keep_headers: bool = None,
    #                       headers: dict = {}):
    #     response = self.writeHtmlToFile(url, file_path, render, session_number, country_code,
    #                                     premium, keep_headers, headers, format='images')
    #     return response

    # def writeDOCXFile(self, url: str, file_path: str, render: bool = None,
    #                   session_number: str = None, country_code: str = None,
    #                   premium: bool = None, keep_headers: bool = None,
    #                   headers: dict = {}):
    #     response = self.writeHtmlToFile(url, file_path, render, session_number, country_code,
    #                                     premium, keep_headers, headers, format='docx')
    #     return response

    # def post(self, url: str, render: bool = None,
    #          session_number: str = None, country_code: str = None,
    #          premium: bool = None, keep_headers: bool = None,
    #          headers: dict = {}):
    #     response = self.getHtml(
    #         url, render, session_number, country_code, premium, keep_headers, headers)
    #     return response

    # def put(self, url: str, render: bool = None,
    #          session_number: str = None, country_code: str = None,
    #          premium: bool = None, keep_headers: bool = None,
    #          headers: dict = {}):
    #     response = self.getHtml(
    #         url, render, session_number, country_code, premium, keep_headers, headers)
    #     return response

    def __prepareRequestUrl(self, **kwargs):
        url_options = {
            'access_token': self.access_token,
            'URL': kwargs['url'],
            'render': 'true' if kwargs['render'] == True else None,
            'session_number': kwargs['session_number'],
            'country_code': kwargs['country_code'],
            'premium': 'true' if kwargs['premium'] == True else None,
            'keep_headers': 'true' if kwargs['keep_headers'] == True else None,
            'format': kwargs['format']
        }
        url_options_filtered = {
            key: value for key, value in
            url_options.items() if value is not None
        }
        option_string = urlencode(url_options_filtered)
        request_url = self.parse_url + '?' + option_string
        return request_url

    def __prepareHeaders(self, custom_headers={}, keep_headers=None):
        headers = {
            'Client': 'NODEJS_CLIENT_LIB',
            'Client-Version': VERSION
        }
        merged_headers = headers.copy()
        merged_headers.update(custom_headers)
        if keep_headers == True:
            return merged_headers
        return headers
