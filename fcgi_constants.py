# https://fastcgi-archives.github.io/FastCGI_Specification.html#S8
# /usr/include/php/main/fastcgi.h

FCGI_VERSION = 1

FCGI_KEEP_CONN = 1

# fcgi_role
FCGI_RESPONDER  = 1
FCGI_AUTHORIZER = 2
FCGI_FILTER     = 3

# fcgi_request_type
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

# Values for protocolStatus member of FCGI_EndRequestBody
FCGI_REQUEST_COMPLETE   = 0
FCGI_CANT_MPX_CONN      = 1
FCGI_OVERLOADED         = 2
FCGI_UNKNOWN_ROLE       = 3
