#!/usr/bin/env python

''' callerid.py is built to automate the change of the callerid in voip.ms web interface as it doesn't support common voip clients caller id delegation well '''

import sys, requests, re

# configuration
username = 'changeme'
password = 'changeme'

# global variables
callerid = ''

# input validation
re_callerid_allowed = re.compile('(\+|[0-9])')
re_callerid_format = re.compile('^(\+|00)[0-9]{8,}$')

# read callerid from command line args
if len(sys.argv) == 2:
    callerid = sys.argv[1].strip()
   
    # strip alle except allowed chars
    callerid = ''.join(re_callerid_allowed.findall(callerid))

    # check whether caller id fits required format
    match = re_callerid_format.match(callerid)

    if match:
        print 'Caller ID: ', match.group()
    else:
        print 'Caller ID does not match required format'
        sys.exit(2)

else:
    print 'Usage: ./callerid.py +41234567890'
    sys.exit(2)

# setup session object (cookiejar)
s = requests.Session()

'''
# DEBUG set proxy and disable TLS verification
s.proxies = { "https" : "https://127.0.0.1:8080" }
s.verify=False
'''

# fetch default login form and default cookie (october_session)
print 'Fetch default page...',
r=s.get('https://voip.ms/login')
print 'ok'

# prepare login params
data={
    'action':'login',
    'lastur':'',
    'col_email': username,
    'col_password': password
}

# authenticate user
print 'Service logon...',
r=s.post(url='https://voip.ms/m/login.php',data=data, allow_redirects=False)

# redirects to /m/index.php if successfull
if r.headers.get('location') == '/m/index.php':
    print 'ok'
else:
    print 'error. login failed. check credentials'
    sys.exit(2)


# prepare caller id params
data={
    'callerid': callerid,
    'button2': 'Apply',
    'action': 'callerid'
}

# update caller ID 
print 'Set caller id...',
r=s.post(url='https://voip.ms/m/settings.php',data=data)

# site confirms with 'Caller id set to...' if successfull
if r.text.find('Caller id set to ') > 0:
    print 'ok'
else: 
    print 'error. unable to set caller'

# logout
print 'Logout...',
r=s.get(url='https://voip.ms/m/logout.php', allow_redirects=False)

# redirects to /m/login.php?logout=true if successfull
if r.headers.get('location') == '/m/login.php?logout=true':
    print 'ok'
    print 'Done.'
else:
    print 'error. logout failed.'

