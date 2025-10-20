# Fxxk_XiaoYoubang

用于友邦远程签到，适用于校友邦小程序V1.6.39。

## 使用方法

> [!IMPORTANT]
>
> 在使用前需阅读并同意[用户协议](https://github.com/gaobobo/Fxxk_XiaoYoubang/wiki/用户协议)。

> [!TIP]
>
> 关于本包的使用方法，参见[clock.py](/src/fxxk_xiaoyoubang/clock.py)

### 安装

- 确保安装了Python 3.10或更高的版本，且`pip`正常工作； 
- 从[本仓库Releases页面](https://github.com/gaobobo/Fxxk_XiaoYoubang/releases)下载发行版。该页面通常附有安装说明，你可以：
  - 使用`pip install <至.whl的路径>`；
  - 使用`pip install <至.whl的URL>`；
- 安装完成后，在控制台输入`fxxk-xyb -h`，如果能正常显示输出，则安装完成。

### 获取微信临时登录码

你需要获取微信的临时登录授权码，该码每5分钟刷新一次，且只能使用一次。获取方法为抓包并拦截对`xcx.xybsyw.com/common/getOpenId.action`的请求。

你可以用任何趁手的工具进行抓包，另提供[参考指南](https://github.com/gaobobo/Fxxk_XiaoYoubang/wiki/截获临时登录凭证)。

### 签到/签退

若要签到，执行：

```shell
fxxk-xyb <临时登录码> <设备品牌> <设备型号> <平台> in --log DEBUG
```

同理，若签退：

```shell
fxxk-xyb <临时登录码> <设备品牌> <设备型号> <平台> in --log DEBUG
```

上述设备信息理论上可以随意填写，但是校友邦会进行记录。建议按实际填写。
