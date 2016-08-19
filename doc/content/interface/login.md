+++
title = "登录"
description = ""
tags = [
    "login",
    "post"
]
date = "2016-04-28"
categories = [
    "user",
    "account",
]

image = "3.png"
toc = true
+++

<font size=2>登录</font>
***

#### API地址：

> /api/login

#### 用户权限：

> Guest


#### Post 数据

[Token]({{< ref "token.md" >}})

{{< highlight html >}}
content = {
    "username" : "YWRtaW4=",
    "password" : "41c88ab8bba1fd171b9063101643fbea"
}

username = base64.encodestring(username)
password = md5('%s:%s'%(user_id, md5('password')))

{{< /highlight >}}



#### 返回值：

类型：[Result]({{< ref "result.md" >}})

