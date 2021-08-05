# https://fastcgi-archives.github.io/FastCGI_Specification.html#S8
# /usr/include/php/main/fastcgi.h
from enum import IntEnum

FCGI_VERSION = 1

FCGI_KEEP_CONN = 1

# fcgi_role
FCGI_RESPONDER  = 1
FCGI_AUTHORIZER = 2
FCGI_FILTER     = 3

# fcgi_request_type
class FCGI_Request_Type(IntEnum):
    FCGI_BEGIN_REQUEST      =  1
    FCGI_ABORT_REQUEST      =  2
    FCGI_END_REQUEST        =  3
    FCGI_PARAMS             =  4
    FCGI_STDIN              =  5
    FCGI_STDOUT             =  6
    FCGI_STDERR             =  7
    FCGI_DATA               =  8
    FCGI_GET_VALUES         =  9
    FCGI_GET_VALUES_RESULT  = 10
    FCGI_UNKNOWN_TYPE       = 11

FCGI_contentData_is_NameValueSequence = {FCGI_Request_Type.FCGI_PARAMS,
                                         FCGI_Request_Type.FCGI_GET_VALUES,
                                         FCGI_Request_Type.FCGI_GET_VALUES_RESULT}

# Values for protocolStatus member of FCGI_EndRequestBody
class FCGI_ProtocolStatus_Value(IntEnum):
    FCGI_REQUEST_COMPLETE   = 0
    FCGI_CANT_MPX_CONN      = 1
    FCGI_OVERLOADED         = 2
    FCGI_UNKNOWN_ROLE       = 3
