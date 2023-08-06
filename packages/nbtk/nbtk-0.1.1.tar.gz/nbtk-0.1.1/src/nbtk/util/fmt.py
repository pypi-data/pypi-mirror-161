import time
import re
from dateutil.parser import parse
from common.log import log_handler

TIMESTAMP_10 = r"^\d{10}(\.\d+)?$"
TIMESTAMP_13 = r"^\d{13}$"

log = log_handler.LogHandler().get_log()

def get_err_msg():
    msg = py_to_java(str({"error_msg": "error in saving and updating", "status": "FAIL"}))
    log.error(msg)
    return msg


def err_formatter(e):
    msg = py_to_java(str({"error_msg": str(e).replace("'", "_").replace('"', "_")}))
    log.error(msg)
    return msg


def format_time(data, pattern):
    if data == None:
        return None

    data = data.replace("年", "-").replace("月", "-").replace(",", ", ")
    data = re.compile(
        r"日|Mon\.|Tue\.|Wed\.|Thur\.|Fri\.|Sat\.|Sun\.|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday").sub(
        "", data)
    if pattern == "timestamp":
        if re.match(TIMESTAMP_10, data):
            ret = data
        elif re.match(TIMESTAMP_13, data):
            ret = int(data) / 1000
        else:
            pattern = "%Y-%m-%d %H:%M:%S"
            ret = time.mktime(time.strptime(parse(data).strftime(pattern), pattern))
        return int(ret)
    else:
        if re.match(TIMESTAMP_10, data):
            return time.strftime(pattern, time.localtime(int(data)))
        elif re.match(TIMESTAMP_13, data):
            return time.strftime(pattern, time.localtime(float(data) / 1000))
        else:
            return parse(data).strftime(pattern)


def py_to_java(s):
    return s.replace("'", '"') \
        .replace("False", "false") \
        .replace("True", "true") \
        .replace(", ", ",") \
        .replace(": ", ":") \
        .replace("None", "null") \
        .replace("nan", "null")
        # .replace("inf", "2147483647")


def java_to_py(java_string):
    py_string = java_string.replace("'", '"')
    return py_string


def cast_float(obj):
    if isinstance(obj, float):
        return round(obj, 3)
    elif isinstance(obj, dict):
        return dict((k, cast_float(v)) for k, v in obj.items())
    elif isinstance(obj, list):
        return list(map(cast_float, obj))
    elif isinstance(obj, tuple):
        return tuple(map(cast_float, obj))
    else:
        return obj


def dup_name_handler(col_name, df_col):
    i = 1
    original_col_name = col_name
    while col_name in df_col:
        col_name = original_col_name + "_" + str(i)
        i += 1
    return col_name
