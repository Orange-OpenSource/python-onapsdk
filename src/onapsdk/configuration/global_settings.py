"""Global settings module."""  # pylint: disable=bad-whitespace


######################
#                    #
# ONAP SERVICES URLS #
#                    #
######################

## API
AAI_URL         = "https://aai.api.sparky.simpledemo.onap.org:30233"
AAI_API_VERSION = "v23"
AAI_AUTH        = "Basic QUFJOkFBSQ=="
CDS_URL         = "http://portal.api.simpledemo.onap.org:30449"
CDS_AUTH        = ("ccsdkapps", "ccsdkapps")
MSB_URL         = "https://msb.api.simpledemo.onap.org:30283"
SDC_BE_URL      = "https://sdc.api.be.simpledemo.onap.org:30204"
SDC_FE_URL      = "https://sdc.api.fe.simpledemo.onap.org:30207"
SDC_AUTH        = "Basic YWFpOktwOGJKNFNYc3pNMFdYbGhhazNlSGxjc2UyZ0F3ODR2YW9HR21KdlV5MlU="
SDNC_URL        = "https://sdnc.api.simpledemo.onap.org:30267"
SDNC_AUTH       = "Basic YWRtaW46S3A4Yko0U1hzek0wV1hsaGFrM2VIbGNzZTJnQXc4NHZhb0dHbUp2VXkyVQ=="
SO_URL          = "http://so.api.simpledemo.onap.org:30277"
SO_API_VERSION  = "v7"
SO_AUTH         = "Basic SW5mcmFQb3J0YWxDbGllbnQ6cGFzc3dvcmQxJA=="
VID_URL         = "https://vid.api.simpledemo.onap.org:30200"
VID_API_VERSION = "/vid"
CLAMP_URL       = "https://clamp.api.simpledemo.onap.org:30258"
CLAMP_AUTH      = "Basic ZGVtb0BwZW9wbGUub3NhYWYub3JnOmRlbW8xMjM0NTYh"
VES_URL         = "http://ves.api.simpledemo.onap.org:30417"
DMAAP_URL       = "http://dmaap.api.simpledemo.onap.org:3904"
NBI_URL         = "https://nbi.api.simpledemo.onap.org:30274"
NBI_API_VERSION = "/nbi/api/v4"
DCAEMOD_URL = ""
HOLMES_URL = "https://aai.api.sparky.simpledemo.onap.org:30293"
POLICY_URL = ""
POLICY_CLAMP_URL = "https://aai.api.sparky.simpledemo.onap.org:30258"

## GUI
AAI_GUI_URL = "https://portal.api.simpledemo.onap.org:30220"
AAI_GUI_SERVICE = "/services/aai/webapp/index.html#/browse"
CDS_GUI_SERVICE = "/"
SO_MONITOR_GUI_SERVICE = "/"
SDC_GUI_SERVICE = "/sdc1/portal"
SDNC_DG_GUI_SERVICE = "/nifi/"
SDNC_ODL_GUI_SERVICE = "/odlux/index.html"

DCAEMOD_GUI_SERVICE = "/"
HOLMES_GUI_SERVICE = "/iui/holmes/default.html"
POLICY_GUI_SERVICE = "/onap/login.html"
POLICY_CLAMP_GUI_SERVICE = "/"
