from metagen.helpers import validate_list_uuid
from uuid import UUID, uuid4


def test_uuid_list_validation():
    assert all(map(lambda x: isinstance(x, UUID), validate_list_uuid([uuid4(), uuid4()])))
    assert all(map(lambda x: isinstance(x, UUID), validate_list_uuid([str(uuid4()), str(uuid4())])))
