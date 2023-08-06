__all__ = ('Tele2Point',)

from phonenumber_field.serializerfields import PhoneNumberField

from expressmoney_service.api import *

_SERVICE = 'services'
_APP = 'tele2'


class _Tele2CreateContract(Contract):
    username = PhoneNumberField()
    first_name = serializers.CharField(max_length=32)
    last_name = serializers.CharField(max_length=32)
    middle_name = serializers.CharField(max_length=32, allow_blank=True)


class _Tele2ID(ID):
    _service = _SERVICE
    _app = _APP
    _view_set = 'tele2'


class Tele2Point(CreatePointMixin, ContractPoint):
    _point_id = _Tele2ID()
    _create_contract = _Tele2CreateContract
