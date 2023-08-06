from .fileawss3testcase import AWSS3FileTestCase
from heaserver.service.testcase.mixin import DeleteMixin, GetAllMixin, GetOneMixin, PutMixin


class TestDeleteFile(AWSS3FileTestCase, DeleteMixin):
    pass


class TestGetFiles(AWSS3FileTestCase, GetAllMixin):
    pass


class TestGetFile(AWSS3FileTestCase, GetOneMixin):
    pass

class TestPutFile(AWSS3FileTestCase, PutMixin):
    pass
