"""
The required configurations for setting up auto-update with name.com
"""

######################################################
#    Settings for Name.com
######################################################

# This is the API interface for name.com.  This script was tested with v4 of their API.
NAME_API_URL = "https://api.name.com/v4/"

# Your FQDN that you would like to keep updated.
FQDN = "test.example.org"

# Username used for authenticating to the name.com API.
USERNAME = "myusername"

# Password used for authenticating to the name.com API.
PASSWORD = "asd321qwe654sdf987cvb654sdfg321sdf654wq"

# Override existing DNS record's TTL value with a new one?  Default: False
TTL_OVERRIDE = False

# TTL value to use for DNS record, assuming override is enabled.  In seconds.
TTL_VALUE = 300



######################################################
#    Settings for IP address validator
######################################################

# IP checker API endpoing full URL
IP_API_URL = "https://api.myip.com"

# IP checker API endpoint IP key name
IP_API_KEY = "ip"




######################################################
#    Settings for this application
######################################################

# Continueously run the script?  Default: Ture
RUN_FOREVER = True

# How often should it run?  (any number in minutes) Default: 10 minutes
RUN_INTERVAL = 10

# Preferred nameserver to test lookups against.  Default: 8.8.8.8
NAMESERVER = "8.8.8.8"
