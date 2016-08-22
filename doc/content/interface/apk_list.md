+++
title = "列出所有安装包"
description = ""
tags = [
    "list",
    "post"
]
date = "2016-08-22"
categories = [
    "user",
    "account",
]

image = "3.png"
toc = true
+++

<font size=2>列出所有安装包</font>
***

#### API地址：

> /api/apk_list/{os_type}

#### 用户权限：

> admin, power user


#### 返回值：

类型：[Result]({{< ref "result.md" >}})

{{< highlight html >}}
content = ["/download/android/iQuran.apk","/download/android/baiduyun.apk"]
{{< /highlight >}}