from collections import namedtuple
import struct

'''
FastCGI specification structs.

A variable length struct VARLENSTRUCT has:
    - a namedtuple assigned to its fixed length prefix, called
        VARLENSTRUCT_Prefix or similar,
    - an unpacking function at VARLENSTRUCT_Prefix.unpack,
    - an asociated VARLENSTRUCT_Nice namedtuple

Each VARLENSTRUCT_Nice named tuple has:
    - a packing function at VARLENSTRUCT_Nice.pack
    - an unpacking function at VARLENSTRUCT_Nice.unpack

VARLENSTRUCT: FCGI_Record, FCGI_NameValuePairXX
'''

# Records
# https://fastcgi-archives.github.io/FastCGI_Specification.html#S3.3
FCGI_Record_Prefix = namedtuple('FCGI_Record_Prefix', 'version type '\
                                                      'requestIdB1 requestIdB0 '\
                                                      'contentLengthB1 contentLengthB0 '\
                                                      'paddingLength reserved ')
FCGI_Record_Prefix.unpack= lambda data : \
                            FCGI_Record_Prefix._make(struct.unpack('8B', data[:8]))

FCGI_Header = FCGI_Record_Prefix

FCGI_Record_Nice = namedtuple('FCGI_Record_Nice', 'version type '\
                                                  'requestId '\
                                                  'contentLength paddingLength '\
                                                  'reserved '\
                                                  'contentData paddingData')

def _FCGI_Record_Nice__pack(fcgi_record_nice):
    content_len = fcgi_record_nice.contentLength
    padding_len = fcgi_record_nice.paddingLength
    return struct.pack(f'>BBHHBB{content_len}s{padding_len}s',
                       *fcgi_record_nice)

def _FCGI_Record_Nice__unpack(data):
    record_prefix = FCGI_Record_Prefix.unpack(data)
    content_len = (record_prefix.contentLengthB1 << 8) + \
                    record_prefix.contentLengthB0
    padding_len = record_prefix.paddingLength
    return FCGI_Record_Nice._make(struct.unpack(f'>BBHHBB{content_len}s{padding_len}s',
                                                 data))

FCGI_Record_Nice.pack = _FCGI_Record_Nice__pack
FCGI_Record_Nice.unpack = _FCGI_Record_Nice__unpack

# Name-Value Pairs
# https://fastcgi-archives.github.io/FastCGI_Specification.html#S3.4
'''
The fields of FCGI_NameValuePair_Prefix are
    nameLengthBH, valueLengthBH
due to the specification distinguishing
between them using the highest byte of those fields.
'''
FCGI_NameValuePair_Prefix = namedtuple('FCGI_NameValuePair_Prefix',
                                       'nameLengthBH valueLengthBH')
FCGI_NameValuePair_Prefix.unpack = lambda data: \
                                    FCGI_NameValuePair_Prefix._make(struct.unpack('BB', data[:2]))

FCGI_NameValuePair11 = namedtuple('FCGI_NameValuePair11', 'nameLengthB0 '\
                                                          'valueLengthB0 '\
                                                          'nameData '\
                                                          'valueData')

FCGI_NameValuePair14 = namedtuple('FCGI_NameValuePair14', 'nameLengthB0 '\
                                                          'valueLengthB3 '\
                                                          'valueLengthB2 '\
                                                          'valueLengthB1 '\
                                                          'valueLengthB0 '\
                                                          'nameData '\
                                                          'valueData')

FCGI_NameValuePair41 = namedtuple('FCGI_NameValuePair44', 'nameLengthB3 '\
                                                          'nameLengthB2 '\
                                                          'nameLengthB1 '\
                                                          'nameLengthB0 '\
                                                          'valueLengthB0 '\
                                                          'nameData '\
                                                          'valueData')

FCGI_NameValuePair44 = namedtuple('FCGI_NameValuePair44', 'nameLengthB3 '\
                                                          'nameLengthB2 '\
                                                          'nameLengthB1 '\
                                                          'nameLengthB0 '\
                                                          'valueLengthB3 '\
                                                          'valueLengthB2 '\
                                                          'valueLengthB1 '\
                                                          'valueLengthB0 '\
                                                          'nameData '\
                                                          'valueData')

FCGI_NameValuePair_Nice = namedtuple('FCGI_NameValuePair_Nice', 'nameLength '\
                                                                'valueLength '\
                                                                'nameData '\
                                                                'valueData')

def _FCGI_NameValuePair_Nice__pack(fcgi_nvpair_nice):
    name_len = fcgi_nvpair_nice.nameLength
    value_len = fcgi_nvpair_nice.valueLength
    tagged_name_len = name_len
    tagged_value_len = value_len
    '''
    Strategy: return the smallest structure possible
    '''
    if name_len > 127: # NameValuePair4x
        tagged_name_len |= 1<<(32-1) # Tag 4 bytes usage
        if value_len > 127: # NameValuePair44
            tagged_value_len |= 1<<(32-1)
            return struct.pack(f'>LL{name_len}s{value_len}s',
                                                       tagged_name_len,
                                                       tagged_value_len,
                                                       *fcgi_nvpair_nice[2:])
        else: # NameValuePair41
            return struct.pack(f'>LB{name_len}s{value_len}s',
                                                       tagged_name_len,
                                                       tagged_value_len,
                                                       *fcgi_nvpair_nice[2:])
    else: # NameValuePair1x
        if value_len > 127: # NameValuePair14
            tagged_value_len |= 1<<(32-1)
            return struct.pack(f'>BL{name_len}s{value_len}s',
                                                       tagged_name_len,
                                                       tagged_value_len,
                                                       *fcgi_nvpair_nice[2:])
        else: # NameValuePair11
            return struct.pack(f'>BB{name_len}s{value_len}s',
                                                       tagged_name_len,
                                                       tagged_value_len,
                                                       *fcgi_nvpair_nice[2:])

def _FCGI_NameValuePair_Nice__unpack(data, return_parsed_bytes=False,
                                           accept_leftovers=False):
    nvpair_prefix = FCGI_NameValuePair_Prefix.unpack(data)
    offset = 2 # Byte index where ~Data parts begins in `data`
    name_len, value_len = None, None
    if nvpair_prefix.nameLengthBH >> 7 == 1 :  # NameValuePair4x
        if nvpair_prefix.valueLengthBH >> 7 == 1 : # NameValuePair44
            name_len, value_len = struct.unpack('>LL', data[:8])
            name_len &= ~(1<<31) # untag MSB
            value_len &= ~(1<<31)
            offset = 8
        else: # NameValuePair41
            name_len, value_len = struct.unpack('>LB', data[:5])
            name_len &= ~(1<<31)
            offset = 5
    else: # NameValuePair1x
        if nvpair_prefix.valueLengthBH >> 7 == 1 : # NameValuePair14
            name_len, value_len = struct.unpack('>BL', data[:5])
            value_len &= ~(1<<31)
            offset = 5
        else: # NameValuePair11
            name_len, value_len = struct.unpack('>BB', data[:2])
            offset = 2
    parsed_bytes = name_len+value_len+offset
    if accept_leftovers and len(data) > parsed_bytes:
        name_data, value_data = struct.unpack(f'{name_len}s{value_len}s',
                                              data[offset:parsed_bytes])
    else:
        name_data, value_data = struct.unpack(f'{name_len}s{value_len}s',
                                              data[offset:])
    nvpair = FCGI_NameValuePair_Nice(nameLength=name_len, valueLength=value_len,
                                     nameData=name_data, valueData=value_data)
    if return_parsed_bytes:
        return nvpair, parsed_bytes
    return nvpair

FCGI_NameValuePair_Nice.pack = _FCGI_NameValuePair_Nice__pack
FCGI_NameValuePair_Nice.unpack = _FCGI_NameValuePair_Nice__unpack


'''
Fixed length structs
'''

# BeginRequest
FCGI_BeginRequestBody = namedtuple('FCGI_BeginRequestBody', 'roleB1 roleB0 '\
                                                            'flags '\
                                                            'reserved')

FCGI_BeginRequestBody.unpack = lambda data: \
                                FCGI_BeginRequestBody._make(struct.unpack('>BBB5s', data))

FCGI_BeginRequestBody_Nice = namedtuple('FCGI_BeginRequestBody_Nice', 'role '\
                                                                      'flags '\
                                                                      'reserved')

FCGI_BeginRequestBody_Nice.pack = lambda fcgi_brbody_nice : \
                                    struct.pack('>HB5s', fcgi_brbody_nice.role,
                                                         fcgi_brbody_nice.flags,
                                       # Reserved only 5 bytes
                                       #struct.pack('>q', fcgi_brbody_nice.reserved)[-5:])
                                       #fcgi_brbody_nice.reserved.rjust(5, b'\x00'))
                                                         fcgi_brbody_nice.reserved)

def _FCGI_BeginRequestBody_Nice__unpack(data):
    brbody = FCGI_BeginRequestBody.unpack(data)
    role = (brbody.roleB1 << 8) | brbody.roleB0
    return FCGI_BeginRequestBody_Nice(role=role, flags=brbody.flags,
                                                 reserved=brbody.reserved)

FCGI_BeginRequestBody_Nice.unpack = _FCGI_BeginRequestBody_Nice__unpack

# EndRequest
FCGI_EndRequestBody = namedtuple('FCGI_EndRequestBody', 'appStatusB3 '\
                                                        'appStatusB2 '\
                                                        'appStatusB1 '\
                                                        'appStatusB0 '\
                                                        'protocolStatus '\
                                                        'reserved')

FCGI_EndRequestBody.unpack = lambda data: \
                              FCGI_EndRequestBody._make(struct.unpack('>5B3s',
                                                                      data))

FCGI_EndRequestBody_Nice = namedtuple('FCGI_EndRequestBody_Nice', 'appStatus '\
                                                                  'protocolStatus '\
                                                                  'reserved')

FCGI_EndRequestBody_Nice.pack = lambda fcgi_erbody_nice : \
                                    struct.pack('>LB3s',
                                                fcgi_erbody_nice.appStatus,
                                                fcgi_erbody_nice.protocolStatus,
                                                fcgi_erbody_nice.reserved)

def _FCGI_EndRequestBody_Nice__unpack(data):
    app_status, protocol_status, reserved = struct.unpack('>LB3s', data)
    return FCGI_EndRequestBody_Nice(appStatus=app_status,
                                   protocolStatus=protocol_status,
                                   reserved=reserved)

FCGI_EndRequestBody_Nice.unpack = _FCGI_EndRequestBody_Nice__unpack
