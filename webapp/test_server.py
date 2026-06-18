# -*- coding: utf-8 -*-
"""Smoke-тест: сервер поднимается, отдаёт страницу и /api/index.
Заодно фиксирует наличие маркера статик-режима в PAGE."""
import json
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

import app


class ServerSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not app.QUESTIONS:
            app.load_questions()
            app.load_kb()
            app.load_java_docs()
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.port = cls.srv.server_address[1]
        cls.t = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.t.start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def _get(self, path):
        with urllib.request.urlopen(
            "http://127.0.0.1:%d%s" % (self.port, path)
        ) as r:
            return r.status, r.read()

    def test_root_has_static_marker(self):
        status, body = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn(b"const STATIC = false;", body)

    def test_api_index_ok(self):
        status, body = self._get("/api/index")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertIn("questions", data)
        self.assertIn("groups", data)


if __name__ == "__main__":
    unittest.main()
