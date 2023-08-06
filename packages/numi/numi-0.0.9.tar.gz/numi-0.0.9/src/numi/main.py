from sys import prefix
from tkinter import BOTH
from numi.utils import base, AT_AF, logger
from numi.handle_input import find_valid_combinations, parse_input_string

logging = logger()


def _get_from_base(n, f):
    """
    Returns all possible variations for the written numbers in the base as a list of strings
    for numbers between 1-19 as well as all numbers that are divisable by 10,100,1000 etc.
    """
    num = base[n, f]
    if "/" in num:
        num = num.split("/")
    else:
        num = [num]

    logging.debug(f"Returning: {num} Input was: {n, f}")
    return num


def _nums_20_99(n, f):
    """
    Returns all possible variations for the written numbers from 20 to 99 as a list of strings.
    """
    n1 = int(str(n)[0] + "0")
    n2 = int(str(n)[1])
    last_number = _get_from_base(n2, f)

    if len(last_number) == 2:
        num = [f"{base[n1,AT_AF]} og {n2}" for n2 in last_number]
    else:
        num = [f"{base[n1,AT_AF]} og {base[n2,f]}"]

    logging.debug(f"Returning: {num} Input was: {n, f}")
    return num


def _nums_100_999(n, f, prefix="both"):
    """
    Returns all possible variations for the written numbers from 100 to 999 as a list of strings.

    prefix values:
        'eitt': Add the word "eitt" infront of "hundrað".
        'hundrað': Return with only "hundrað".
        'both': Return with both "hundrað" and "eitt hundrað".

    """

    def _hundreds(n):
        n_1 = int(str(n)[0])
        if n_1 == 1:
            num = f"{base[n_1, 'et_hk_nf']} hundrað"
        elif n_1 in [2, 3, 4]:
            num = f"{base[n_1,'ft_hk_nf']} hundruð"
        else:
            num = f"{base[n_1,AT_AF]} hundruð"
        logging.debug(f"Returning: {num} Input was: {n}")
        return num

    n1 = int(str(n)[0] + "00")
    num1 = _hundreds(n1)
    n2 = n - n1
    num2 = []

    if n in [100, 200, 300, 400, 500, 600, 700, 800, 900]:
        num = [_hundreds(n)]

    elif n2 in [x for x in range(1, 20)] or n2 in [x for x in range(20, 101, 10)]:
        for line in _get_from_base(n2, f):
            num2.append(f"og {line}")
        num2 = num2
    else:
        num2 = _nums_20_99(n2, f)

    if num2:
        num = [f"{num1} {n2}" for n2 in num2]

    if prefix == "both":
        for line in num:
            if "eitt hundrað" in line:
                num.append(line.replace("eitt hundrað", "hundrað"))
    if prefix == "hundrað":
        for idx, line in enumerate(num):
            if "eitt hundrað" in line:
                num[idx] = line.replace("eitt hundrað", "hundrað")
    logging.debug(f"Returning: {num} Input was: {n, f}")
    return num


def _nums_1000_9999(n, f, add_thousand=True):
    """
    Returns all possible variations for the written numbers from 1000 to 9999 as a list of strings.
    """

    def _thousands(n):
        n_1 = int(str(n)[0])
        if n_1 == 1:
            num = f"{base[n_1, 'et_hk_nf']} þúsund"
        elif n_1 in [2, 3, 4]:
            num = f"{base[n_1,'ft_hk_nf']} þúsund"
        else:
            num = f"{base[n_1,AT_AF]} þúsund"
        logging.debug(f"Returning: {num} Input was: {n}")
        return num

    n1 = int(str(n)[0] + "000")
    num1 = _thousands(n1)
    n2 = n - n1
    num2 = []
    if n in [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000]:
        num = [_thousands(n)]
    elif n2 < 1000 and n2 > 100:
        num2 = _nums_100_999(n2, f, prefix="eitt")
    elif n2 in [x for x in range(1, 20)] or n2 in [x for x in range(20, 101, 10)]:
        for line in _get_from_base(n2, f):
            num2.append(f"og {line}")
    else:
        num2 = _nums_20_99(n2, f)

    if num2:
        num = [f"{num1} {n2}" for n2 in num2]

    if n == 1000 and add_thousand:
        for line in num:
            if "eitt þúsund" in line:
                num.append(line.replace("eitt þúsund", "þúsund"))

    logging.debug(f"Returning: {num} Input was: {n, f}")
    return num


def _nums_10000_99999(n, f):
    """
    Returns all possible variations for the written numbers from 10000 to 99999 as a list of strings.
    """
    num = []
    num1 = int(str(n)[0:-3])
    num2 = int(str(n)[-3:])

    if n in [10000]:
        return [f"{x} þúsund" for x in divert(num1, f)]

    # Numbers 10000-99999
    if num1 in [x for x in range(10, 21)] or num1 in [x for x in range(20, 101, 10)]:
        # print(1, num1)
        f1 = AT_AF
    elif int(str(num1)[-1]) == 1:
        # print(2, num1)
        f1 = "et_hk_nf"

    elif int(str(num1)[-1]) in [2, 3, 4]:
        # print(3, num1)
        f1 = "ft_hk_nf"
    else:
        # print(4, num1)
        f1 = AT_AF

    for line in divert(num2, f, prefix="eitt"):
        # Some numbers have an "og" between num1 and num2
        last_two = int(str(num2)[-2:])
        if last_two in [x for x in range(0, 20)] or last_two in [
            x for x in range(20, 91, 10)
        ]:
            num.append(f"{divert(num1, f1, prefix='hundrað')[0]} þúsund og {line}")
        else:
            num.append(f"{divert(num1, f1, prefix='hundrað')[0]} þúsund {line}")
    logging.debug(f"Returning: {num} Input was: {n, f}")
    return num


def _nums_100000_999999(n, f):
    """
    Returns all possible variations for the written numbers from 100000 to 999999 as a list of strings.
    """
    num = []
    num1 = int(str(n)[0:-3])
    num2 = int(str(n)[-3:])

    if n in [100000]:
        return [f"{x} þúsund" for x in divert(num1, f)]

    # Numbers 100000-999999
    if int(str(num1)[-2:]) in [x for x in range(10, 20)] or int(str(num1)[-2:]) in [
        x for x in range(20, 101, 10)
    ]:
        # print(1, num1)
        f1 = AT_AF
    elif int(str(num1)[-1]) == 1:
        # print(2, num1)
        f1 = "et_hk_nf"

    elif int(str(num1)[-1]) in [2, 3, 4]:
        # print(3, num1)
        f1 = "ft_hk_nf"
    else:
        # print(4, num1)
        f1 = AT_AF

    for line in divert(num2, f, prefix="eitt"):
        # Some numbers have an "og" between num1 and num2
        # Numbers 1-9
        if len(str(num2)) == 1:
            logging.debug(f'1: Adding "og" {{num2}}')
            num.append(f"{divert(num1, f1, prefix='hundrað')[0]} þúsund og {line}")
        elif (
            len(str(num2)) == 2
            and num2 in [x for x in range(20, 91, 10)]
            or num2 in range(10, 20)
        ):
            logging.debug(f'2: Adding "og" {num2}')
            num.append(f"{divert(num1, f1, prefix='hundrað')[0]} þúsund og {line}")
        else:
            logging.debug(f'3: Not adding "og" {num2}')
            num.append(f"{divert(num1, f1, prefix='hundrað')[0]} þúsund {line}")
    logging.debug(f"Returning: {num} Input was: {n, f}")
    return num


def divert(n, f, prefix="both"):
    """
    Handles user input and returns a list of string with all
    possible variations of if input number
    """
    logging.debug(f"User input: {n,f}")
    # Numbers 1-19 add 20, 30, 40, 50, 60, 70, 80, 90
    if n in [x for x in range(1, 20)] or n in [x for x in range(20, 91, 10)]:
        return _get_from_base(n, f)
    # Numbers 20 to 99
    elif n in [x for x in range(20, 100)]:
        return _nums_20_99(n, f)
    # Numbers from 100 to 999
    elif len(str(n)) == 3:
        return _nums_100_999(n, f, prefix)
    # Numbers between 1000 and 9999
    elif len(str(n)) == 4:
        return _nums_1000_9999(n, f)
    # Nmnbers between 10000 and 999999
    elif len(str(n)) == 5:
        return _nums_10000_99999(n, f)
    # Nmnbers between 100000 and 9999999
    elif len(str(n)) == 6:
        return _nums_100000_999999(n, f)


def spell_out(n, f=None):
    """
    Validates user input and sends the input to diverter.
    The output is printed to the console.
    """
    logging.debug(f"User input: {n,f}")
    f = parse_input_string(f)
    logging.debug(
        f"The the len of f after parse input is {len(f)} and of type {type(f)}"
    )

    f = find_valid_combinations(n, f)

    if len(f) > 1:
        return [[n, v, divert(n, v)] for v in f]
    else:
        return divert(n, f[0])
