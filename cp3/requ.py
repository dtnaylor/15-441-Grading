#!/usr/bin/python
import requests
BAD_POST_DATA = 'asldksjdklfjaskldfjlksdjgjksdhfjkgdhjkfshcvkljsdclkmzxvm,xcnm,vnsdilfuodghiouwerhfguiohsdiourghiousdrhguio'

s = requests.Session()
prepped = requests.Request('GET', 'http://127.0.0.1:%d/index.html' % 12347).prepare()
prepped.prepare_headers({'Con\r\n\r\nnection':'Cl\r\nwose'})
#prepped.prepare_body(BAD_POST_DATA, '')
#prepped.headers['Content-Length'] = -1000
print prepped.headers
print prepped.body
response = s.send(prepped, timeout=10.0)
print response.status_code
#pAssertEqual(200, response.status_code)
