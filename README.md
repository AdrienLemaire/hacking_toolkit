# hacking_toolkit

**requirements:**

* Python 3
* python-requests


## SQL Injection

### blind_get_list_data.py
* Works on MySQL >= 5.
* Requires a vulnerable url with get param, and an expected string from normal result
* Uses bitwise operations to retrieve a character in 8 requests.

An url is vulnerable to this exploit if:

* Normal request `http://172.28.128.3:8007/membre.php?id=7` returns results
* Request `http://172.28.128.3:8007/membre.php?id=7' and 1='1` also
  returns results.
* But request `http://172.28.128.3:8007/membre.php?id=7' and 1='0`
  doesn't return any results.

This allows us to ask many yes/no questions to MySQL, and figure out table
names, columns names and data.
