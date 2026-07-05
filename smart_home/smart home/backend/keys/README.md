# JWT RSA keys

正式启用 RSA 时，在本目录放置：

```text
private_key.pem
public_key.pem
```

当前如果文件不存在，开发环境会自动退回 HS256 mock secret，方便先跑通接口。

私钥不要提交到 Git。