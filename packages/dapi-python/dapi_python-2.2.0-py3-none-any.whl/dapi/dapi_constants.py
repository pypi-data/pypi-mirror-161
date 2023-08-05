from collections import namedtuple

dapi_api_statuses = dict(
    FAILED='failed',
    DONE='done',
    USER_INPUT_REQUIRED='user_input_required',
)

DapiStatus = namedtuple("DapiStatus", dapi_api_statuses.keys())(
    *dapi_api_statuses.values())


dapi_input_types = dict(
    OTP='otp',
    PIN='pin',
    SECRET_QUESTION='secret_question',
    CAPTCHA='captcha',
    CONFIRMATION='confirmation',
    TOKEN='token',
)

DapiInputType = namedtuple("DapiInputType", dapi_input_types.keys())(
    *dapi_input_types.values())

dapi_beneficiary_types = dict(
    LOCAL='local',
    SAME='same',
    INTL='intl',
)

DapiBeneficiaryType = namedtuple("DapiBeneficiaryType", dapi_beneficiary_types.keys())(
    *dapi_beneficiary_types.values())
