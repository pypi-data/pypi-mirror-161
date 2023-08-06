__all__ = ('SmsMTSPoint', 'SmsMTS2Point')

from expressmoney_service.api import *

_SERVICE = 'services'


class _SmsMTSCreateContract(Contract):
    message = serializers.CharField(max_length=60)


class _SmsMTS2CreateContract(Contract):
    message = serializers.CharField(max_length=60)


class _SmsMTSResponseContract(_SmsMTSCreateContract):
    pass


class _SmsMTSID(ID):
    _service = _SERVICE
    _app = 'sms_mts'
    _view_set = 'sms_mts'


class _SmsMTS2ID(ID):
    _service = _SERVICE
    _app = 'sms_mts'
    _view_set = 'sms_mts2'


class SmsMTSPoint(ResponseMixin, CreatePointMixin, ContractPoint):
    _point_id = _SmsMTSID()
    _create_contract = _SmsMTSCreateContract
    _response_contract = _SmsMTSResponseContract


class SmsMTS2Point(CreatePointMixin, ContractPoint):
    _point_id = _SmsMTS2ID()
    _create_contract = _SmsMTS2CreateContract
