# ClashV

#### 介绍
Linux桌面版的clash

#### 软件架构
软件架构说明

#### 安装教程

1.  上传到Linux系统中后，执行安装命令：./setup.sh ins
2.  卸载，执行命令：./setup.sh unins

#### 使用说明

1.  可以通过订阅链接更新配置信息
2.  如果网络不通的情况下订阅信息会加载失败，加载成功后就可以关闭窗口
3.  可以输入ssr的链接格式转化成可以配置

#### clash基本用法

1.  启动命令：./clash -d ~/.config/clash/
2.  停止命令：ps -ef |grep 'clash' |grep -v grep |awk '{print $2}' |xargs kill -9

注：配置信息参考config.yaml文件
    
    规则解释

    DOMAIN-SUFFIX：域名后缀匹配
    DOMAIN：域名匹配
    DOMAIN-KEYWORD：域名关键字匹配
    IP-CIDR：IP段匹配
    SRC-IP-CIDR：源IP段匹配
    GEOIP：GEOIP数据库（国家代码）匹配
    DST-PORT：目标端口匹配
    SRC-PORT：源端口匹配
    MATCH：全匹配（一般放在最后）

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request
    https://etproxypool.ga/clash/config