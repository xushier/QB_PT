# coding=utf-8
# Created By Xushier  QQ:1575659493

import time

def mbytes_to_bytes(mbytes, return_type='int'):

    if isinstance(mbytes, (str,int)):
        mbytes = float(mbytes)

    if return_type == 'int':
        return int(mbytes*1048576)
    else:
        return str(int(mbytes*1048576))

def gbytes_to_bytes(gbytes, return_type='int'):

    if isinstance(gbytes, (str,int)):
        gbytes = float(gbytes)

    if return_type == 'int':
        return int(gbytes*1073741824)
    else:
        return str(int(gbytes*1073741824))

def bytes_to_mbytes(bytes, return_type='float'):

    if isinstance(bytes, str):
        bytes = int(bytes)
    
    if return_type == 'float':
        return round(bytes / 1048576, 2)
    else:
        return str(round(bytes / 1048576, 2))

def bytes_to_gbytes(bytes, return_type='float'):

    if isinstance(bytes, str):
        bytes = int(bytes)
    
    if return_type == 'float':
        return round(bytes / 1073741824, 2)
    else:
        return str(round(bytes / 1073741824, 2))

def timestamp_to_date(timestamp, return_format='%Y-%m-%d %H:%M:%S') -> str:

    if isinstance(timestamp, str) or isinstance(timestamp, float):
        timestamp = int(timestamp)

    return time.strftime(return_format, time.localtime(timestamp))

def date_to_timestamp(date:str, input_format='%Y-%m-%d %H:%M:%S', return_type='int'):

    struct_time = time.strptime(date, input_format)

    if return_type == 'str':
        return str(int(time.mktime(struct_time)))
    else:
        return int(time.mktime(struct_time))

def olddate_to_newdate(date:str, input_format='%Y-%m-%d %H:%M:%S', return_format='%Y-%m-%d %H:%M:%S') -> str:

    if input_format == return_format:
        return date
    else:
        struct_time = time.strptime(date, input_format)
        return time.strftime(return_format, struct_time)
    