## 构建信息

|     版本     |   指针   |   日期    |
|:----------:|:------:|:-------:|
| ${version} | ${ref} | ${date} |



---

## 安装

```shell
pip install ${link}
```

> [!IMPORTANT]
> 
> - 不含任何依赖项。这些依赖项会从PyPI自动下载。请自行使用镜像站进行加速。
> - docker守护进程`fxxk_xiaoyoubang_docker`需要额外安装依赖，使用下列命令安装：
> ```shell
> pip install "fxxk_xiaoyoubang[docker] @ ${link}"
> ```

> [!TIP]
> 
> 默认包含主模块`fxxk_xiaoyoubang`与docker守护进程`fxxk_xiaoyoubang_docker`。
> 主版本号代表主模块、版本号注释docker代表docker守护进程的版本。
