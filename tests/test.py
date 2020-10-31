from D365BCAPI.D365BC16API import Connect
from unittest import TestCase, mock
import json

class D365BCAPITestCase(TestCase):

    def test_read(self):
        with mock.patch('D365BCAPI.D365BC16API.requests') as mocked_req:
            mocked_req.get.return_value.status_code = 200
            t = Connect('http://test.lt/test', auth={'a':'a'}, headers= {'some headers'})
            t.filter_text = "aa eq bb"
            mocked_req.get.return_value.json = {"value": [{"@odata.etag":"etag"}]}
            re = t.read()
            mocked_req.get.assert_called_with('http://test.lt/test', params='$filter=aa eq bb',
                                              auth={'a':'a'}, headers= {'some headers'})
            re = t.read()
            mocked_req.get.assert_called_with('http://test.lt/test', params=None,
                                              auth={'a':'a'}, headers= {'some headers'})
            self.assertEqual(re, [{'@odata.etag': 'etag'}])

    def test_insert(self):
        with mock.patch('D365BCAPI.D365BC16API.requests') as mocked_req:
            mocked_req.post.return_value.status_code = 201
            mocked_req.post.return_value.reason = 'reason'
            t = Connect('http://test.lt/test', auth={'a':'a'}, headers= {'some headers'})
            re = t.insert({"orderid":"123456"})
            mocked_req.post.assert_called_with('http://test.lt/test', auth={'a':'a'},
                                              headers= {'some headers'}, json= {"orderid":"123456"})
            self.assertEqual(re, [201, 'reason'])

if __name__ == '__main__':
    TestCase.main()
