+++
title = "列出所有用户"
description = ""
tags = [
    "list",
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

<font size=2>列出所有用户信息</font>
***

#### API地址：

> /api/accounts

> /api/accounts/{group_id}

#### 用户权限：

> admin, power user


#### 返回值：

类型：[Result]({{< ref "result.md" >}})

{{< highlight html >}}
content = [{
    "nick_name" : "admin",
    "_id" : "admin",
    "avatar" : "",
    "desc":"",
    "source":"local",
    "join_time" : 1457958007295
}]
{{< /highlight >}}