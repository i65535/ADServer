+++
title = "删除用户分组"
description = ""
tags = [
    "delete",
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

<font size=2>删除指定命名空间下的用户分组，如果分组下还有用户，返回失败</font>
***

#### API地址：

> /api/group/delete/{group_id}

#### 用户权限：

> admin

#### Post 数据

[Token]({{< ref "token.md" >}})


#### 返回值：

类型：[Result]({{< ref "result.md" >}})
