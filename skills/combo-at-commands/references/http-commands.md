# HTTP指令

## 4.4.1 AT+HTTPCLIENTLINE — HTTP/HTTPS请求（单行模式）

### 发送: AT+HTTPCLIENTLINE=<transport_type>,<opt>,<content-type>,<host>,<port>,<path>[,<data>]

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| transport_type | 整数 | 是 | 1：HTTP，2：HTTPS | 传输类型 |
| opt | 整数 | 是 | 2：GET，3：POST | 请求方式 |
| content-type | 字符串 | 是 | application/x-www-form-urlencoded、application/json、multipart/form-data、text/xml、text/html | 仅POST生效，GET时不生效，可以填写任意字符串 |
| host | 字符串 | 是 | — | 服务器域名或IP（如www.baidu.com或192.168.1.100） |
| port | 整数 | 是 | — | 端口号（HTTP缺省值80，HTTPS缺省值443） |
| path | 字符串 | 是 | — | HTTP(S)路径，缺省值"/" |
| data | 字符串 | 否 | — | 请求携带的数据。当opt为GET时携带在path中，格式符合HTTP格式要求（?key1=value1&key2=value2...）；当opt为POST时为POST携带的主体 |

**响应：**
```
Responselength:<len>    // response body数据长度
<response>              // 获取的响应数据
OK                      // 请求成功
```

**示例：**
```
// HTTP GET
AT+HTTPCLIENTLINE=1,2,,www.baidu.com,,

// HTTPS GET
AT+HTTPCLIENTLINE=2,2,,www.baidu.com,,

// HTTP POST
AT+HTTPCLIENTLINE=1,3,,192.168.2.253,8080,/test,"{\"OTP\":\"test\"}"
```

---

## 4.4.2 AT+HTTPRAW — HTTP/HTTPS请求（长数据模式）

### 发送: AT+HTTPRAW=<transport_type>,<opt>,<content-type>,<host>,<port>,<path>,<len>

| 参数 | 类型 | 必选 | 取值范围 | 说明 |
|------|------|:---:|----------|------|
| transport_type | 整数 | 是 | 1：HTTP，2：HTTPS | 传输类型 |
| opt | 整数 | 是 | 2：GET（暂时不支持），3：POST | 请求方式 |
| content-type | 字符串 | 是 | application/x-www-form-urlencoded、application/json、multipart/form-data、text/xml、text/html | 仅POST生效，GET时不生效，可以填写任意字符串 |
| host | 字符串 | 是 | — | 服务器域名或IP（如www.baidu.com或192.168.1.100） |
| port | 整数 | 是 | — | 端口号（HTTP缺省值80，HTTPS缺省值443） |
| path | 字符串 | 是 | — | HTTP(S)路径，缺省值"/" |
| len | 整数 | 是 | — | 需要接收的数据长度 |

**响应：**
```
>                   // 收到这个字符之后开始输入要发送的数据
<response>          // 响应数据
OK                  // 请求成功
```

**示例：**
```
// HTTP POST（发送5字节数据）
AT+HTTPRAW=1,3,"application/json",192.168.1.199,8080,/test,5
>
hello              // 输入5字节data数据
Testack             // 获取响应
OK                  // 获取完毕
```
