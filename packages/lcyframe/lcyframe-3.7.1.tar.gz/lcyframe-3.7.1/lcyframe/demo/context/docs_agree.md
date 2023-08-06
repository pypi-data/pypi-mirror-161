<!--
文档约定说明内容

修改文件名或者删除文件，框架会采用默认文件代替

在遵循markdown格式的前提下，允许修改以下内容
-->

## 一、约定说明
### 1.1 参数说明

**请求方式：本框架规定了所有请求参数所配置的方式以及用途：**

|参数位置|Content-Type|举个例子|说明|
|---|---|---|---|
|path|--|/url/{user}/{uid}|拼接在url内|
|query|--|/url/user?uid=10|拼接在?后|
|body|application/x-www-form-urlencoded|{"uid": 100, "sex": 1}|表单提交，推荐|
|body|multipart/form-data|{"file": open("demo.jpg"), "header": open("header.jpg")}|上传文件|
|body|application/json|'uid=100&sex=1'或'{"uid":100,"sex:1"}'|json提交|
|body|text/plain|'uid=100&sex=1'或'{"uid":100,"sex:1"}'|--|

**Restful请求示例：**
~~~python
### Send POST request with body as form parameters
POST https://domain.com/post
Content-Type: application/x-www-form-urlencoded

{
  "id": 999,
  "value": "content"
}

### Send POST request with json body
POST https://domain.com/post
Content-Type: application/json

id=999&value=content

### Send a form with the text and file fields
POST https://domain.com/post
Content-Type: multipart/form-data; boundary=WebAppBoundary

--WebAppBoundary
Content-Disposition: form-data; name="element-name"
Content-Type: text/plain

Name
--WebAppBoundary
Content-Disposition: form-data; name="data"; filename="data.json"
Content-Type: application/json

< ./request-form-data.json
--WebAppBoundary--

###
~~~

**参数值类型：在设置schema.yml时，指定type的值允许是以下几种之一**

|类型|说明|
|---|---|
| int | 整形|
| float | 浮点型|
| str | 字符串|
| list | 数组（不推荐)|
| json | json串|
| file | 文件|

### 1.2 headers
API请求时，需要提供请求头

headers：
~~~python
{
    "uid": "10000，注册成功、登录成功后返回",
    "token": "授权码, 注册成功、登录成功后返回",
    "locale": "cn",
    "lang": "",
    "version": "默认 1.0", 
    "bundle": "",
    "platform": 0 IOS, 1 Android,
    "os": "",
    "device_id": ""
}
~~~
### 1.3 API 请求结果
当`HTTP_CODE=200`时，代表本次请求响应成功，响应结构如下所示：
~~~python
{
  "error": 0, 
  "msg": msg, 
  "data": {}
}
~~~

>`error`: 当`error=0`时，代表API处理成功，客户端可以正常处理data；当`error!=0`时，代表API处理失败，error即为对应的异常码
>
>`msg`: 字段为本次请求的提示信息。当`error=0`时，`msg=ok`；当`error!=0`时，`msg=ErrorName`
>
>`data`: 为本次API返回的数据，如{'nickname'：'昵称', 'sex'：1}。在接口文档中，不同的API所返回的结构不同,具体详见《接口说明》

当`HTTP_CODE!=200`时，如`404`、`405`、`500`的错误码，客户端按需处理

### 1.4 双向校验码seq生成
部分防刷接口需要提供参数seq，生成方法如下

salt：写死在客户端
~~~
例如：
params={"nickname": "阿刘", "age": "111", "timestamp": 1473761433}
上述2个参数value 均为 utf-8 编码, 根据key的字典顺序排序 键和值之间用"="连接 键值对之间用"&"连接,
生成待校验的字符串string, string 与 salt 字符串 拼接,计算校验码：
seq = md5(salt + "nickname=阿刘&age=111&timestamp=1473761433")
注：凡需要传seq的接口，必须同时提供请求时间戳参数：timestamp
~~~

### 1.5 翻页码规则：仅支持查看下一页，不支持跳页
参数名：last_id，由服务器返回。客户端可以在请求列表时，回传给服务端，
~~~
    1、当不提供该参数时，代表查看第一页
    2、当服务端返回last_id=-1时，代表没有下一页了
~~~

### 1.6 域名配置
**本地环境：**
> 1、api：http://192.168.2.50:6700  
> 2、docs文档：http://192.168.2.50:6779

**测试环境：**
> 1、api：http://192.168.2.140:6700  
> 2、docs文档：http://192.168.2.140:6779

### 1.7、免责声明
本框架仅能在取得足够合法授权的企业安全建设中使用，在使用本过程中，您应确保自己所有行为符合当地的法律法规。 
如您在使用本工具的过程中存在任何非法行为，您将自行承担所有后果，开发者不承担任何法律及连带责任。 
除非您已充分阅读、完全理解并接受本协议所有条款，否则，请您不要安装并使用本框架。
您的使用行为或者您以其他任何明示或者默示方式表示接受本协议的，即视为您已阅读并同意本协议的约束。
