# HTTP指令

## 4.4.1 AT+HTTPCLIENTLINE — HTTP/HTTPS请求（单行模式）

### 发送: AT+HTTPCLIENTLINE=<transport_type>,<opt>,<content-type>,<host>,<port>,<path>[,<data>]

| 参数 | 说明 |
|------|------|
| transport_type | 1=HTTP，2=HTTPS |
| opt | 2=GET，3=POST |
| content-type | 仅POST生效，GET时可填任意字符串。参考类型：application/x-www-form-urlencoded, application/json, multipart/form-data, text/xml, text/html |
| host | 服务器域名或IP（如www.baidu.com或192.168.1.100） |
| port | 端口号（HTTP缺省80，HTTPS缺省443） |
| path | HTTP(S)路径，缺省"/" |
| data | GET时为path中的查询参数（?key1=value1&key2=value2...）；POST时为请求主体 |

| 响应 | `Responselength:<len>` / `<response>` / OK |

**示例：**
```
// HTTP GET
AT+HTTPCLIENTLINE=1,2,,www.baidu.com,,

// HTTPS GET
AT+HTTPCLIENTLINE=2,2,,www.baidu.com,,

// HTTP POST
AT+HTTPCLIENTLINE=1,3,,192.168.2.253,8080,/test,"{\"OTP\":\"test\"}"
```

## 4.4.2 AT+HTTPRAW — HTTP/HTTPS请求（长数据模式）

### 发送: AT+HTTPRAW=<transport_type>,<opt>,<content-type>,<host>,<port>,<path>,<len>

| 参数 | 说明 |
|------|------|
| transport_type | 1=HTTP，2=HTTPS |
| opt | 2=GET（暂时不支持），3=POST |
| content-type | 仅POST生效。参考类型同AT+HTTPCLIENTLINE |
| host | 服务器域名或IP |
| port | 端口号（HTTP缺省80，HTTPS缺省443） |
| path | HTTP(S)路径，缺省"/" |
| len | 需要接收的数据长度 |

| 响应 | `>` → 输入数据 → `<response>` → OK |

**示例：**
```
// HTTP POST（发送5字节数据）
AT+HTTPRAW=1,3,"application/json",192.168.1.199,8080,/test,5
>
hello
Testack    // 获取响应
OK         // 获取完毕
```
