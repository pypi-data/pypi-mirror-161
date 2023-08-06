__all__ = ('EsiaPoint',)

from phonenumber_field.serializerfields import PhoneNumberField

from expressmoney_service.api import *

_SERVICE = 'services'
_APP = 'idx_esia'


class _EsiaCreateContract(Contract):
    phonenumber = PhoneNumberField()
    first_name = serializers.CharField(max_length=32)
    last_name = serializers.CharField(max_length=32)
    middle_name = serializers.CharField(max_length=32)
    birth_date = serializers.DateField()
    passport_serial = serializers.CharField(max_length=4)
    passport_number = serializers.CharField(max_length=6)


class _EsiaID(ID):
    _service = _SERVICE
    _app = _APP
    _view_set = 'esia'


class EsiaPoint(CreatePointMixin, ContractPoint):
    _point_id = _EsiaID()
    _create_contract = _EsiaCreateContract
