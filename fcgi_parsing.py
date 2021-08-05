from fcgi_structs import *
from fcgi_constants import *

'''
Packs and unpacks streams of bytes from and into the namedtuple structs.

These functions should be preferred when dealing with raw data, instead of the
pack/unpack functions from fcgi_structs.
'''

def fcgi_parse_record_stream(data):
    data_len = len(data)
    offset = 0
    while offset < data_len:
        nice_record, parsed_bytes = FCGI_Record_Nice.unpack(data[offset:],
                                                            return_parsed_bytes=True,
                                                            accept_leftovers=True)
        nice_parsed_record = fcgi_parse_nice_record(nice_record)
        offset += parsed_bytes
        yield nice_parsed_record

def fcgi_parse_nice_record(nice_record):
    '''
    Given a FCGI_Record_Nice nice_record, returns a new FCGI_Record_Nice
    nice_parsed record, but:
        - its type field is replaced from a raw int to an FCGI_Request_Type IntEnum
        - if its type is in the FCGI_contentData_is_NameValueSequence set, its
          contentData field is replaced from a byte string into a list of
          FCGI_NameValuePair_Nice objects.
    '''
    meaningful_type = FCGI_Request_Type(nice_record.type)
    content_data = nice_record.contentData
    if meaningful_type in FCGI_contentData_is_NameValueSequence:
        content_data = list(fcgi_parse_namevalue_stream(nice_record.contentData,
                                                        nice_record.contentLength))
    nice_parsed_record = FCGI_Record_Nice(nice_record.version,
                                          meaningful_type,
                                          nice_record.requestId,
                                          nice_record.contentLength,
                                          nice_record.paddingLength,
                                          nice_record.reserved,
                                          content_data,
                                          nice_record.paddingData)
    return nice_parsed_record

def fcgi_parse_namevalue_stream(contentData, content_len=None):
    if content_len is None:
        content_len = len(contentData)

    offset = 0
    while offset < content_len:
        nvpair, parsed_bytes = FCGI_NameValuePair_Nice.unpack(contentData[offset:],
                                                              return_parsed_bytes=True,
                                                              accept_leftovers=True)
        offset += parsed_bytes
        yield nvpair

def fcgi_build_namevalue_stream(nvpair_list):
    for nvpair in nvpair_list:
        yield FCGI_NameValuePair_Nice.pack(nvpair)

def fcgi_build_record_stream(record_list):
    for nice_record in record_list:
        content_data = nice_record.contentData
        if nice_record.type in FCGI_contentData_is_NameValueSequence:
            content_data = b''.join(fcgi_build_namevalue_stream(nice_record.contentData))
        yield FCGI_Record_Nice.pack(FCGI_Record_Nice(nice_record.version,
                                                     nice_record.type,
                                                     nice_record.requestId,
                                                     nice_record.contentLength,
                                                     nice_record.paddingLength,
                                                     nice_record.reserved,
                                                     content_data,
                                                     nice_record.paddingData))

# For testing
to_bytes = lambda s: b''.join(list(map(lambda x: chr(int(x, 16)).encode('latin_1'), s.split(' '))))

'''
If `ls` is a valid list of FCGI_Record_Nice objects, then:
list(fcgi.fcgi_parse_record_stream( b''.join(fcgi.fcgi_build_record_stream(ls)) )) == ls
'''
