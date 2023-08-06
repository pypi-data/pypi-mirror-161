__all__ = ('NoLoanPoint', 'SmsPoint')

from phonenumber_field.serializerfields import PhoneNumberField

from expressmoney_service.api import *

_SERVICE = 'services'
_APP = 'server1c'


class _NoLoanCreateContract(Contract):
    passport_serial = serializers.CharField(max_length=4)
    passport_number = serializers.CharField(max_length=6)


class _SmsCreateContract(Contract):
    phonenumber = PhoneNumberField()
    message = serializers.CharField(max_length=60)


class _NoLoanID(ID):
    _service = _SERVICE
    _app = _APP
    _view_set = 'no_loan'


class _SmsID(ID):
    _service = _SERVICE
    _app = _APP
    _view_set = 'sms'


class NoLoanPoint(CreatePointMixin, ContractPoint):
    _point_id = _NoLoanID()
    _create_contract = _NoLoanCreateContract


class SmsPoint(CreatePointMixin, ContractPoint):
    _point_id = _SmsID()
    _create_contract = _SmsCreateContract
