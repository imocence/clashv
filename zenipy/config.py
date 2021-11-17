#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import io
import yaml
import logback

HOME = os.getenv("HOME")
YAML_PATH = os.path.join(HOME, ".config/clash/config.yaml")
CONF_PATH = os.path.join(HOME, ".config/clash/config_url")
logger = logback.Logger()


# 读取yaml文件
def get_yaml_data(yaml_file):
    # 打开yaml文件
    print("***获取yaml文件数据***")
    file_yaml = io.open(yaml_file, 'r', encoding="utf-8")
    file_data = file_yaml.read()
    file_yaml.close()
    logger.info("Yaml file of type: {}".format(type(file_data)))
    # 将字符串转化为字典或列表
    print("***转化yaml数据为字典或列表***")
    data = yaml.load(file_data, Loader=yaml.FullLoader)
    logger.info("Returns the data type: {}".format(type(data)))
    return data


# 下载config
def download_yaml(url):
    if 'http' not in url:
        url = 'https://free886.herokuapp.com/clash/config'
    logger.info('Download config url: {}'.format(url))
    url_file = os.popen('curl {}'.format(url)).read()
    if 'mode:' in url_file:
        with open(YAML_PATH, "wb") as f:
            f.write(url_file)
        write_url(url)
        url_file.close()
        return None
    else:
        return 1


# 将url写入文件
def write_url(url):
    with open(CONF_PATH, "w") as f:
        f.write(url)
    logger.info('Write url to a file: {}'.format(url))
    return None


# 从文件中读出url
def read_url():
    with open(CONF_PATH, "a+") as f:
        f.seek(0)
        url = f.readline()
    logger.info('Read the url from a file: {}'.format(url))
    return url


# 设置代理参数
def set_proxy():
    host = '127.0.0.1'
    data = get_yaml_data(YAML_PATH)
    port = data['port'] if data.has_key('port') else 7890
    s_port = data["socks-port"] if data.has_key('socks-port') else 7891
    logger.info('agent_host: {},agent_port: {},agent_socks_port: {}'.format(host, port, s_port))
    os.system('gsettings set org.gnome.system.proxy.http  host {}'.format(host))
    os.system('gsettings set org.gnome.system.proxy.http  port {}'.format(port))
    os.system('gsettings set org.gnome.system.proxy.https host {}'.format(host))
    os.system('gsettings set org.gnome.system.proxy.https port {}'.format(port))
    os.system('gsettings set org.gnome.system.proxy.ftp   host {}'.format(host))
    os.system('gsettings set org.gnome.system.proxy.ftp   port {}'.format(port))
    os.system('gsettings set org.gnome.system.proxy.socks host {}'.format(host))
    os.system('gsettings set org.gnome.system.proxy.socks port {}'.format(s_port))
    os.system('gsettings set org.gnome.system.proxy mode  "manual"')
    logger.info('Agent started')


# 取消代理参数
def set_none_proxy():
    os.system('gsettings set org.gnome.system.proxy mode "none"')
    logger.info('Agent cleared')
