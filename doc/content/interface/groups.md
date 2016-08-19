+++
title = "列出命名空间下的全部用户组"
description = ""
tags = [
    "list",
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
<font size=2>列出命名空间下的全部用户组</font>
***

#### API地址：

> /api/groups

> /api/groups/{namespace}

#### 分别实现：

* 查询全部的用户组，不区分命名空间
* 查询命名空间下的全部用户组

#### 用户权限：

> admin, power user, user


#### Post 数据

[Token]({{< ref "token.md" >}})



#### 返回值：

类型：[Result]({{< ref "result.md" >}})

{{< highlight html >}}
content = [{
    "_id":1,
    "group_name":"dev",
    "namespace":"appsoar",
    "create_time": 13423423423,
    "desc":""
}]
{{< /highlight >}}
