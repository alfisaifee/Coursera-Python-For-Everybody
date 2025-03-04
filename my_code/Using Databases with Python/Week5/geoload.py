# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 08:08:23 2019

@author: User
"""

import urllib.request, urllib.parse, urllib.error
import http
import ssl
import json
import sqlite3
import time
import sys

api_key = False

if api_key is False:
    api_key = 42
    service_url = "http://py4e-data.dr-chuck.net/json?"
else :
    service_url = "https://maps.googleapis.com/maps/api/geocode/json?"

conn = sqlite3.connect('geodata_test.sqlite')
cur = conn.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT)')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

fh = open(r'\Users\User\Desktop\Coursera PFE\my_code\where.data')
count = 0
for line in fh:
    if count > 200:
        print('Retrieved 200 locations, restart to retrieve more')
        break
    
    address = line.strip()
    print('')
    cur.execute('SELECT geodata FROM Locations WHERE address = ?',(memoryview(address.encode()),))
    try:
        data = cur.fetchone()[0]
        print("Found in database ",address)
        continue
    except:
        pass
    
    parms = dict()
    parms['address'] = address
    if api_key is not False: parms['key'] = api_key
    url = service_url + urllib.parse.urlencode(parms)
    
    print('Retrieving', url)
    uh = urllib.request.urlopen(url,context=ctx)
    data = uh.read().decode()
    print('Retrieved', len(data), 'characters', data[:20].replace('\n', ' '))
    count = count + 1
    
    try:
        js = json.loads(data)
    except:
        print(data)  # We print in case unicode causes an error
        continue
    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') :
        print('==== Failure To Retrieve ====')
        print(data)
        break

    cur.execute('''INSERT INTO Locations (address, geodata)
            VALUES ( ?, ? )''', (memoryview(address.encode()), memoryview(data.encode()) ) )
    conn.commit()
    if count % 10 == 0 :
        print('Pausing for a bit...')
        time.sleep(5)

print("Run geodump.py to read the data from the database so you can vizualize it on a map.")

    

