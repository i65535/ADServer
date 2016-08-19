+++
title = "更新分组信息"
description = ""
tags = [
    "update",
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
<font size=2>更新分组信息</font>
***

#### API地址：

> /api/group/update/{group_id}

#### 用户权限：

> admin

#### Post 数据

[Token]({{< ref "token.md" >}})

{{< highlight html >}}
Group = {
    "group_name":"dev",
    "namespace":"appsoar",
    "desc":"",
}
{{< /highlight >}}

#### 返回值：

类型：[Result]({{< ref "result.md" >}})
