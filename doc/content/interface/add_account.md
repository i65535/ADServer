+++
title = "创建用户"
description = ""
tags = [
    "add",
    "post"
]
date = "2016-04-05"
categories = [
    "user",
    "account",
]

image = "3.png"
toc = true
+++

<font size=2>创建用户</font>
***

#### API地址：

> /api/account/add

#### 用户权限：

> admin


#### Post 数据

[Token]({{< ref "token.md" >}})

{{< highlight html >}}
User = {
    "_id":"admin",
    "password":"admin",
    "nick_name":"admin",
    "role":"ring0",  // ring0, ring5
    "desc":"",
    "source":"local",
    "avatar":""
}
{{< /highlight >}}


#### 返回值：

类型：[Result]({{< ref "result.md" >}})

