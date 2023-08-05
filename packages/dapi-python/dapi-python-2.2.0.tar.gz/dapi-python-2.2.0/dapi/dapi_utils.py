import random
import re
import string

from dapi.dapi_constants import DapiBeneficiaryType


def generate_random_string(length=5):
    letters_and_digits = string.ascii_letters + string.digits
    random_string = ''.join((random.choice(letters_and_digits)
                             for i in range(length)))
    return random_string


def truncate_string(string, limit):
    if len(string) <= limit:
        return string

    random_suffix = generate_random_string(5)
    return string[0:(limit - 5)] + random_suffix


def truncate_key_value(key_validator_props, key, beneficiary_array):
    if ('required' in key_validator_props and key_validator_props['required']) or (
            'optional' in key_validator_props and key_validator_props[
        'optional'] and key in beneficiary_array) or key in beneficiary_array:
        if key not in beneficiary_array or not beneficiary_array[key]:
            raise Exception(f"{key} is missing")

        if 'length' in key_validator_props and key_validator_props['length'] > 0 and key_validator_props['length'] < len(
                beneficiary_array[key]):
            beneficiary_array[key] = truncate_string(
                beneficiary_array[key], key_validator_props['length'])

        if 'allowedCharacters' in key_validator_props:
            output = re.search(
                key_validator_props['allowedCharacters'], beneficiary_array[key])
            if output is not None:
                output = output.group(0)
                beneficiary_array[key] = output
            else:
                #   This should only happen if you send a string that contains only special characters
                raise Exception(
                    f"Unable to truncate string value to invalid parameter -  {key}")

    return beneficiary_array[key] if key in beneficiary_array else None


def validate_key_value(key_validator_props, key, beneficiary_array):
    if ('required' in key_validator_props and key_validator_props['required']) or (
            'optional' in key_validator_props and key_validator_props[
        'optional'] and key in beneficiary_array) or key in beneficiary_array:
        if key not in beneficiary_array or not beneficiary_array[key]:
            raise Exception(f"{key} is missing")

        if 'length' in key_validator_props and key_validator_props['length'] > 0 and key_validator_props['length'] < len(
                beneficiary_array[key]):
            raise Exception(
                f"{key}  is too long. Maximum length: {key_validator_props['length']}. But got length: {len(beneficiary_array[key])}")

        if 'allowedCharacters' in key_validator_props:
            output = re.search(
                key_validator_props['allowedCharacters'], beneficiary_array[key])
            if output is None:
                raise Exception(
                    f"{key}  should not contain special characters")

    return beneficiary_array[key] if key in beneficiary_array else None


def validateCreateBeneficiary(validator, beneficiary):
    beneficiary_type = beneficiary.get('type', None)
    if not beneficiary_type:
        raise Exception("type is missing")
    elif beneficiary_type is not DapiBeneficiaryType.LOCAL and beneficiary_type is not DapiBeneficiaryType.SAME:
        raise Exception("type has to be local or same")

    validator_props = validator['createBeneficiary'][
        beneficiary_type] if 'createBeneficiary' in validator and beneficiary_type in validator['createBeneficiary'] else []
    for key in validator_props:
        if key == 'address' and key in beneficiary:
            for propKey in validator_props[key]:
                if propKey != 'length':
                    truncated_value = validate_key_value(
                        validator_props[key][propKey], propKey, beneficiary[key])
                    if key in beneficiary:
                        beneficiary[key][propKey] = truncated_value
        else:
            truncated_value = validate_key_value(
                validator_props[key], key, beneficiary)
            if key in beneficiary:
                beneficiary[key] = truncated_value
    return beneficiary


def truncateCreateBeneficiary(validator, beneficiary):
    beneficiary_type = beneficiary.get('type', None)
    if not beneficiary_type:
        raise Exception("type is missing")
    elif beneficiary_type is not DapiBeneficiaryType.LOCAL and beneficiary_type is not DapiBeneficiaryType.SAME:
        raise Exception("type has to be local or same")

    validator_props = validator['createBeneficiary'][
        beneficiary_type] if 'createBeneficiary' in validator and beneficiary_type in validator['createBeneficiary'] else []
    for key in validator_props:
        if key == 'address' and key in beneficiary:
            for propKey in validator_props[key]:
                if propKey != 'length':
                    truncated_value = truncate_key_value(
                        validator_props[key][propKey], propKey, beneficiary[key])
                    if key in beneficiary:
                        beneficiary[key][propKey] = truncated_value

        else:
            truncated_value = truncate_key_value(
                validator_props[key], key, beneficiary)
            if key in beneficiary:
                beneficiary[key] = truncated_value
    return beneficiary
