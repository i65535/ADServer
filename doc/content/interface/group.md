+++
title = "取得用户组详细信息"
description = ""
tags = [
    "detail",
    "get"
]
date = "2016-04-05"
categories = [
    "group",
    "account",
]

image = "3.png"
toc = true
+++
<font size=2>取得用户组详细信息</font>
***

#### API地址：

> /api/group/{group_id}

#### 用户权限：

> admin, power user, user

#### Post 数据

[Token]({{< ref "token.md" >}})


#### 返回值：

类型：[Result]({{< ref "result.md" >}})

{{< highlight html >}}
content = {
    "_id":1,
    "group_name":"dev",
    "namespace":"appsoar",
    "create_time": 13423423423,
    "desc":""
}
{{< /highlight >}}
