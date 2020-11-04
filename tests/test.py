from D365BCAPI.D365BCv1API import Connect
from unittest import TestCase, mock
import json

class D365BCAPITestCase(TestCase):

    def test_read_OK(self):
        with mock.patch('D365BCAPI.D365BCv1API.requests') as mocked_req:
            mocked_req.get.return_value.status_code = 200
            r = Connect('http://test.lt/test', auth={'a':'a'}, headers= {'some headers'})
            r.filter_text = "aa eq bb"
            respo= r.read() #  execute with filter
            mocked_req.get.assert_called_with('http://test.lt/test', params='$filter=aa eq bb',
                                              auth={'a':'a'}, headers= {'some headers'})
            respo = r.read() #  execute without filter
            mocked_req.get.assert_called_with('http://test.lt/test', params=None,
                                              auth={'a':'a'}, headers= {'some headers'})

    def test_read_Fail(self):
        with mock.patch('D365BCAPI.D365BCv1API.requests') as mocked_req:
            mocked_req.get.return_value.status_code = 200
            mocked_req.get.return_value.status_code = 400 #  Check if return error
            mocked_req.get.return_value.reason = 'Any error reason' #  error message
            r = Connect('http://test.lt/test', auth={'a':'a'}, headers= {'some headers'})
            respo = r.read() # execute and receive error
            self.assertEqual(respo, [], 'read: on error response must be []') #  check if reponse is empty
            self.assertEqual(r.except_error, [400, 'Any error reason'], 'read: on error variable except_error '
                                                                        'must to include error code and reason')

    def test_insert_OK(self):
        with mock.patch('D365BCAPI.D365BCv1API.requests') as mocked_req:
            mocked_req.post.return_value.status_code = 201
            mocked_req.post.return_value.reason = 'Created'
            ins = Connect('http://test.lt/test', auth={'a':'a'}, headers= {'some headers'})
            respo = ins.insert({"orderid":"123456"})
            mocked_req.post.assert_called_with('http://test.lt/test', auth={'a':'a'},
                                              headers= {'some headers'}, json= {"orderid":"123456"})
            self.assertEqual(respo, [201, 'Created'], 'insert: no error returns [201, Created] ') #  without error

    def test_insert_FAIL(self):
        with mock.patch('D365BCAPI.D365BCv1API.requests') as mocked_req:
            #  any error
            mocked_req.post.return_value.status_code = 400
            mocked_req.post.return_value.reason = 'Any error reason' #  error message
            ins = Connect('http://test.lt/test', auth={'a':'a'}, headers= {'some headers'})
            respo = ins.insert({"orderid":"123456"})
            self.assertEqual(respo, [], 'insert: on error return must be blank') #  return blank if error
            self.assertEqual(ins.except_error, [400, 'Any error reason'], 'Insert: on error variable except_error '
                                                                        'must to include error code and reason')

    def test_delete_OK(self):
        with mock.patch('D365BCAPI.D365BCv1API.requests') as mocked_req:
            mocked_req.get.return_value.status_code = 200
            mocked_req.delete.return_value.status_code = 204
            mocked_req.delete.return_value.reason = 'OK'
            dele = Connect('http://test.lt/test(123456789abcd)', auth={'a':'a'}, headers= {'some headers'})
            respo = dele.delete()
            mocked_req.delete.assert_called_with('http://test.lt/test(123456789abcd)', auth={'a':'a'},
                                              headers= {'some headers'})
            self.assertEqual(respo, [204, 'OK'], 'delete: no error - returns [204, OK]')

            #  any error
    def test_delete_FAIL(self):
        with mock.patch('D365BCAPI.D365BCv1API.requests') as mocked_req:
            mocked_req.get.return_value.status_code = 200
            mocked_req.delete.return_value.status_code = 400
            mocked_req.delete.return_value.reason = 'Any error reason' #  error message
            dele = Connect('http://test.lt/test(123456789abcd)', auth={'a':'a'}, headers= {'some headers'})
            respo = dele.delete()
            self.assertEqual(respo, [], 'delete: on error returns blank')
            self.assertEqual(dele.except_error, [400, 'Any error reason'], 'delete: on error variable except_error '
                                                                        'must to include error code and reason')

    def test_modify_OK(self):
        with mock.patch('D365BCAPI.D365BCv1API.requests') as mocked_req:
            mocked_req.get.return_value.status_code = 200
            mocked_req.patch.return_value.status_code = 200
            mocked_req.patch.return_value.reason = 'OK'
            modi = Connect('http://test.lt/test(123456789abcd)', auth={'a':'a'}, headers= {'some headers'})
            respo = modi.modify(json_body= {"orderid":"123456"})
            mocked_req.patch.assert_called_with('http://test.lt/test(123456789abcd)', auth={'a':'a'},
                                              headers= {'some headers'}, json= {"orderid":"123456"})
            self.assertEqual(respo, [200, 'OK'], 'modify: no error - returns [204, OK]')

            #  any error
    def test_modify_FAIL(self):
        with mock.patch('D365BCAPI.D365BCv1API.requests') as mocked_req:
            mocked_req.get.return_value.status_code = 200
            mocked_req.patch.return_value.status_code = 400
            mocked_req.patch.return_value.reason = 'Any error reason' #  error message
            modi= Connect('http://test.lt/test(123456789abcd)', auth={'a':'a'}, headers= {'some headers'})
            respo = modi.modify(json_body= {"orderid":"123456"})
            self.assertEqual(respo, [], 'modify: on error returns blank')
            self.assertEqual(modi.except_error, [400, 'Any error reason'], 'modify: on error variable except_error '
                                                                        'must to include error code and reason')

    def test_exe_OK(self):
        with mock.patch('D365BCAPI.D365BCv1API.requests') as mocked_req:
            mocked_req.post.return_value.status_code = 204
            mocked_req.post.return_value.reason = 'No content'
            ex = Connect('http://test.lt/test(123456789abcd)/NAV.Action', auth={'a':'a'}, headers= {'some headers'})
            respo = ex.exe()
            mocked_req.post.assert_called_with('http://test.lt/test(123456789abcd)/NAV.Action', auth={'a':'a'},
                                              headers= {'some headers'}, json=None)
            self.assertEqual(respo, [204, 'No content'], 'execution: no error returns [204, No content] ') #  without error

            #  any error
    def test_exe_FAIL(self):
        with mock.patch('D365BCAPI.D365BCv1API.requests') as mocked_req:
            mocked_req.post.return_value.status_code = 400
            mocked_req.post.return_value.reason = 'Any error reason' #  error message
            ex = Connect('http://test.lt/test(123456789abcd)/NAV.Action', auth={'a':'a'}, headers= {'some headers'})
            respo = ex.exe()
            self.assertEqual(respo, [], 'insert: on error return must be blank') #  return blank if error
            self.assertEqual(ex.except_error, [400, 'Any error reason'], 'Execute: on error variable except_error '
                                                                        'must to include error code and reason')


if __name__ == '__main__':
    TestCase.main()
