from rest_framework.test import APITestCase

class BaseAPITestCase(APITestCase):

    def assertResponseRaiseCode(self, response, code):
        self.assertEqual(response.data.get('error_code'), code, response.data)