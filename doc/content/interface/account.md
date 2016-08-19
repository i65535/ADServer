+++
title = "取得用户详细信息"
description = ""
tags = [
    "detail",
    "get"
]
date = "2016-04-05"
categories = [
    "user",
    "account",
]

image = "3.png"
toc = true
+++

<font size=2>取得用户详细信息,包含密码</font>

***

#### API地址：

> /api/account/{user_id}

#### 用户权限：

> admin, power user, user

#### Post 数据

[Token]({{< ref "token.md" >}})

#### 返回值：

类型：[Result]({{< ref "result.md" >}})

{{< highlight html >}}
content = {
    "user_id" : "admin",
    "nick_name" : "admin",
    "avatar" : "",
    "desc":"",
    "source":"local",
    "password" : "$2a$10$f4UrYQDuijGdWkxO0GTA5uyHwjExLVll/o6Bdg629qfiFctqzijZW",
    "join_time" : 1457958007295
}
{{< /highlight >}}