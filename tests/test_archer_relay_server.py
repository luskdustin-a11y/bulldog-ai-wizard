import http.client
import json
import secrets
import threading
import unittest
from archer_relay_server import create_server
from archer_secure_transport import make_packet

class RelayServerTests(unittest.TestCase):
    def setUp(self):
        self.secret=secrets.token_bytes(32)
        self.server,self.receiver=create_server(self.secret,{"VAL"})
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def post(self,packet,path="/v1/events"):
        conn=http.client.HTTPConnection("127.0.0.1",self.server.server_address[1],timeout=2)
        conn.request("POST",path,json.dumps(packet),{"Content-Type":"application/json"})
        res=conn.getresponse()
        status=res.status
        body=json.loads(res.read()) if status!=404 else None
        conn.close()
        return status,body

    def test_valid_signed_message(self):
        event={"id":"1","source":"VAL","department":"Shop","payload":"ok"}
        status,body=self.post(make_packet(self.secret,event))
        self.assertEqual(status,200)
        self.assertEqual(body,{"accepted":True})
        self.assertEqual(len(self.receiver.messages),1)

    def test_bad_signature(self):
        event={"id":"1","source":"VAL","department":"Shop","payload":"ok"}
        status,_=self.post(make_packet(secrets.token_bytes(32),event))
        self.assertEqual(status,403)

    def test_duplicate_id_not_reprocessed(self):
        event={"id":"1","source":"VAL","department":"Shop","payload":"ok"}
        packet=make_packet(self.secret,event)
        self.post(packet)
        self.post(packet)
        self.assertEqual(len(self.receiver.messages),1)

    def test_public_bind_disallowed(self):
        with self.assertRaises(ValueError):
            create_server(self.secret,{"VAL"},host="0.0.0.0")
