# zmcli 命令行工具

## 安装

zmcli 基于 Python3 编写，所以需首先安装 Python3 环境。

`pip3 install zmcli`

> 一般情况 `pip` 的安装路径为 `/usr/bin` 但是公司发的最新机器使用 `pip3` 命令安装到了 `~/Library/Python/3.8/bin` 目录下，这种情况需在 `~/.zshrc` 文件中加入 `export PATH=$HOME/bin:~/Library/Python/3.8/bin:/usr/local/bin:$PATH` 命令行程序才可正常执行，否则会报 `Command not found` 的错误。

## 使用

基本命令可通过 `zmcli -h` 查看帮助菜单

首次运行时，请按提示输入你的 Artifacory 的 User Name 和 API Key，这两个参数会保存成一个配置文件，在 `~/.zmcli_conf` 文件中。

### 示例

**在工程目录下执行**

```bash
feature
├── Bin
├── client
├── common
├── dependencies
├── ltt
├── mac-client
├── thirdparties
├── vendors
└── zoombase
```

例如工程目录结构如上，则需在 feature 目录下执行 `zmcli` 命令

#### 切换所有仓库到指定分支

`zmcli checkou-all client-5.x-release`

#### 查看某个 repo 下 build 列表

`zmcli show-builds feature-client-5.12 --arch mac_arm64 --num 3`

`--arch` 指定架构，默认为 `mac_x86_64`

`--num` 指定显示多少条数据，默认值为 `10`

```bash
+------------------------------------------------------+
|   Latest builds for feature-client-5.12(mac_arm64)   |
+-------------+---------------------------+------------+
|   Version   |         Created At        | Arch_type  |
+-------------+---------------------------+------------+
|  5.12.0.491 |  2022-07-20T06:23:35.683Z | mac_arm64  |
|  5.12.0.484 |  2022-07-19T06:49:09.939Z | mac_arm64  |
|  5.12.0.461 |  2022-07-13T09:18:49.346Z | mac_arm64  |
+-------------+---------------------------+------------+
```

#### 回滚到某一次 Build 的 commit 并替换 lib

`zmcli rollback feature-client-5.12 --arch mac_arm64 --build 5.12.0.491`

`--build` 回滚到指定 Build，若不指定，则回滚到当前 Repo 的最新 Build

`--arch` 指定架构，默认为 `mac_x86_64`

#### 所有仓库切换到某分支，拉取最新代码并替换该分支下的最新 lib

`zmcli update-all feature-client-5.12 --arch mac_arm64`

`--arch` 指定架构，默认为 `mac_x86_64`

