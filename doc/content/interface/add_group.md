+++
title = "创建用户分组"
description = ""
tags = [
    "add",
    "post"
]
date = "2016-04-05"
categories = [
    "group",
    "account",
]

image = "3.png"
toc = true
+++
<font size=2>创建用户分组</font>
***

#### API地址：

> /api/group/add

#### 用户权限：

> admin

#### Post 数据

[Token]({{< ref "token.md" >}})

{{< highlight html >}}
Group = {
    "_id":1,
    "group_name":"dev",
    "namespace":"appsoar",
    "desc":"",
}
{{< /highlight >}}

#### 返回值：

类型：[Result]({{< ref "result.md" >}})
