+++
title = "接口鉴权"
description = ""
tags = [
    "token"
]
date = "2016-04-05"
categories = [
    "parameter"
]

image = "3.png" 
toc = true
+++

<font size=2>检查请求合法性</font>
***

#### token数据结构：

{{< highlight html >}}
{
    "timestamp":"1354591574485",
    "uuid":"test",
    "hash":"ZTU1ZmIwOWE2OTY4MGNiMTBlZmZhZDE0ZjIxZjk2ZTdmOTc4YjVlYQ=="
}
{{< /highlight >}}

<!--more-->

#### Python 实现方式

{{< highlight html >}}
import time
import base64
import hmac
import sha

def get_token(self,method,access_uuid,access_key):
    timestamp = long(time.time() * 1000)
    msg = "<%d><%s>"%(timestamp,method)
    access_key = str(access_key)
    
    token = {}
    token["timestamp"] = str(timestamp)
    token["hash"] = base64.encodestring(hmac.new(access_key, msg, sha).hexdigest()).strip()
    token["uuid"] = access_uuid
    return token
{{< /highlight >}}

#### Javascript 实现方式

{{< highlight html >}}

<script src="js/CryptoJS/crypto-sha1-hmac/crypto-sha1-hmac.js" type="text/javascript"></script>
<script src="js/CryptoJS/crypto-sha256-hmac/crypto-sha256-hmac.js" type="text/javascript"></script>

function getToken(MethodName,access_uuid,access_key){
var getSecKey =function(method,key,timestamp){
    msg = "<"+timestamp+"><"+ method+">";
    var hmac = Crypto.HMAC(Crypto.SHA1, msg, key);
    return Base64.encode(hmac);
}
return {'timestamp':new Date().getTime(),
    'uuid':access_uuid,
    'hash':getSecKey(MethodName,access_key,timestamp)}
}
{{< /highlight >}}
