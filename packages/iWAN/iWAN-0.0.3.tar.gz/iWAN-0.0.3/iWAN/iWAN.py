# encoding=utf8
import hmac
import json
import base64
import collections
import time
from websocket import create_connection #https://pypi.org/project/websocket_client/
import copy

class iWAN:
    def __init__(self,url,secretkey,Apikey):
        self.url = url
        self.secretkey = secretkey
        self.Apikey = Apikey

    #gettimestamp
    def get_timestamp(self):
        timestamp = int(round(time.time() * 1000))
        return timestamp

    #signature function,to make sure the request_src is the dict type
    def gensig(self,request_src):
        message = json.dumps(request_src,separators=(',',':'))
        hamc_src = hmac.new(bytes(self.secretkey, encoding='utf-8'),bytes(message, encoding='utf-8'),digestmod='sha256')
        sig = base64.b64encode(hamc_src.digest()).decode('utf-8')
        return sig

    def gen_api_request(self,request_src):
        '''
        :param request_src: dict type
        :param secretkey:
        :return:
        '''
        timestamp = self.get_timestamp()      #get current timestamp
        request_src_dic = collections.OrderedDict(request_src)     #transfer json string to python dic object
        request_src_dic['params']['timestamp'] = timestamp
        sig = self.gensig(request_src_dic)
        request_src_dic['params']['signature'] = sig
        request_data = json.dumps(request_src_dic,separators=(',', ':'))#remove the characters 'space 'which is round at the ',' and ':', to ovoid generate the signature
        return request_data

    def sendRequest(self,request_src,reTry=10):
        '''
        :param request_src: i.e
        {}
        :param reTry:
        :return:
        '''
        n=reTry
        request = copy.deepcopy(request_src)
        while n:
            try:
                ws = create_connection(self.url + self.Apikey, timeout=30)
                ws.send(self.gen_api_request(request))
                rsp = ws.recv()
                rsp_dic = json.loads(rsp)
                return rsp_dic
            except Exception as e:
                n-=1
                if n ==0:
                    rsp_dic = {'result': 'Error {}'.format(str(e))}
                    return  rsp_dic


if __name__ == '__main__':
    request_src = {"jsonrpc":"2.0","method":"getBalance","params":{"address":"0x8b157B3fFEAD48C8a4CDC6bddBE1C1D170049Da4", "chainType":"WAN"},"id":1}
    url = 'wss://apitest.wanchain.org:8443/ws/v3/'
    secretkey = '0ead74a31cb'
    Apikey = '1bd599a317'
    iwan = iWAN(url,secretkey,Apikey)
    print(json.dumps(iwan.sendRequest(request_src)))
