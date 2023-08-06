import re

from core.number.BigFloat import BigFloat


def crack_to_serialize(bigfloat: BigFloat):
    if str(bigfloat) == '0.0':
        return 0, 0, 0
    (number_str, decimal_str) = bigfloat.crack()
    match_leading_zeros = re.search('(^0+)', decimal_str)
    decimal_leading_zeros = len(match_leading_zeros.group(1)) if match_leading_zeros else 0
    return int(number_str), int(decimal_str), decimal_leading_zeros


def join_to_deserialize(number, decimal, leading_decimal_zeros):
    complete_number = f'{number}.{decimal}'
    if leading_decimal_zeros > 0:
        zero_padding = ''.rjust(leading_decimal_zeros, '0')
        complete_number = f'{number}.{zero_padding}{decimal}'
    return BigFloat(complete_number)
