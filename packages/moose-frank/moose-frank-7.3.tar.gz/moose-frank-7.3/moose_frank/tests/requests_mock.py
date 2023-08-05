from typing import ClassVar

import requests_mock


class RequestMockMixin:
    m: ClassVar[requests_mock.Mocker] = None

    @classmethod
    def setUpClass(cls):
        cls.m = requests_mock.Mocker()
        cls.m.start()

        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.m.stop()
        super().tearDownClass()
