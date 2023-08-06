from unittest import TestCase
from quickscraper_sdk import QuickScraper
# from time import time
import tests.constant as constant


class Testing(TestCase):

    def test_parse_url(self):
        quickscraper_client = QuickScraper(constant.ACCESS_TOKEN)
        request_url = constant.SAMPLE_REQUEST_URL_FOR_HTML
        response = quickscraper_client.getHtml(request_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.text)

    def test_dummy_token(self):
        quickscraper_client = QuickScraper('DUMMY')
        request_url = constant.SAMPLE_REQUEST_URL_FOR_HTML
        response = quickscraper_client.getHtml(request_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.text, 'Please enter valid access token')

    def test_render_true(self):
        quickscraper_client = QuickScraper(constant.ACCESS_TOKEN)
        request_url = constant.SAMPLE_REQUEST_URL_FOR_HTML
        response = quickscraper_client.getHtml(request_url, render=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.text)

    def test_custom_headers(self):
        quickscraper_client = QuickScraper(constant.ACCESS_TOKEN)
        request_url = constant.SAMPLE_REQUEST_URL_HEADER
        options = {
            'X-Custom-Header-Key-1': 'THIS_IS_CUSTOM_HEADER_1',
            'Qs-Custom-Header-Key': 'THIS_IS_QS_CUSTOM_HEADER'
        }
        response = quickscraper_client.getHtml(
            request_url, keep_headers=True, headers=options)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.text)
        self.assertIn('headers', response.text)
        self.assertIn('X-Custom-Header-Key-1', response.text)
        self.assertIn('THIS_IS_CUSTOM_HEADER_1', response.text)
        self.assertIn('Qs-Custom-Header-Key', response.text)
        self.assertIn('THIS_IS_QS_CUSTOM_HEADER', response.text)

    # def test_session_number(self):
    #     quickscraper_client = QuickScraper(constant.ACCESS_TOKEN)
    #     request_url = constant.SAMPLE_REQUEST_URL_FOR_HTML
    #     session_number = 'QS-' + str(int(time()))
    #     response = quickscraper_client.getHtml(
    #         request_url, session_number=session_number)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsNotNone(response.text)

    def test_country_code(self):
        quickscraper_client = QuickScraper(constant.ACCESS_TOKEN)
        request_url = constant.SAMPLE_REQUEST_URL_FOR_HTML
        response = quickscraper_client.getHtml(request_url, country_code='US')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.text)

    def test_premium_proxy(self):
        quickscraper_client = QuickScraper(constant.ACCESS_TOKEN)
        request_url = constant.SAMPLE_REQUEST_URL_FOR_HTML
        response = quickscraper_client.getHtml(request_url, premium=True)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.text)

    def test_write_html_to_file(self):
        quickscraper_client = QuickScraper(constant.ACCESS_TOKEN)
        request_url = constant.SAMPLE_REQUEST_URL_FOR_HTML
        response = quickscraper_client.writeHtmlToFile(request_url, 'test.log')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.text)

    # def test_write_csv_file(self):
    #     quickscraper_client = QuickScraper(constant.ACCESS_TOKEN)
    #     request_url = constant.SAMPLE_REQUEST_URL_FOR_CSV
    #     response = quickscraper_client.writeCSVFile(request_url, 'test.csv')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsNotNone(response.text)

    # def test_get_all_images_in_zip(self):
    #     quickscraper_client = QuickScraper(constant.ACCESS_TOKEN)
    #     request_url = constant.SAMPLE_REQUEST_URL_FOR_ZIP
    #     response = quickscraper_client.getAllImagesInZip(
    #         request_url, 'test.zip')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsNotNone(response.text)

    # def test_write_docx_file(self):
    #     quickscraper_client = QuickScraper(constant.ACCESS_TOKEN)
    #     request_url = constant.SAMPLE_REQUEST_URL_FOR_DOCX
    #     response = quickscraper_client.writeDOCXFile(request_url, 'test.docx')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsNotNone(response.text)

    # def test_post(self):
    #     quickscraper_client = QuickScraper(constant.ACCESS_TOKEN)
    #     request_url = constant.SAMPLE_REQUEST_URL_FOR_HTML
    #     response = quickscraper_client.getHtml(request_url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsNotNone(response.text)

    # def test_put(self):
    #     quickscraper_client = QuickScraper(constant.ACCESS_TOKEN)
    #     request_url = constant.SAMPLE_REQUEST_URL_FOR_HTML
    #     response = quickscraper_client.getHtml(request_url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsNotNone(response.text)
