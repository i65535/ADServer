+++
title = "删除用户"
description = ""
tags = [
    "delete",
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

<font size=2>删除用户，同时移除用户加入的用户组信息，如果用户名下还有仓库，或用户不存在，则删除失败</font>
***

#### API地址：

> /api/account/delete

#### 用户权限：

> admin

#### Post 数据

[Token]({{< ref "token.md" >}})

{{< highlight html >}}
filter = [{
    "_id":'user_id'
}]

#### 返回值：

类型：[Result]({{< ref "result.md" >}})

