#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import io
import sys
import yaml
import logback
import requests

reload(sys)
sys.setdefaultencoding('utf-8')

HOME = os.getenv("HOME")
YAML_PATH = os.path.join(HOME, ".config/clash/config.yaml")
CONF_PATH = os.path.join(HOME, ".config/clash/config_url")
logger = logback.Logger()


# 获取链接文本
def get_base_file(url):
    try:
        html = requests.get(url)
        html.raise_for_status
        html.encoding = html.apparent_encoding
    except IOError as ioe:
        logger.info('getBasefile Error:', ioe)
    else:
        logger.info('html encode: {}, system encode: {}'.format(html.encoding, sys.getdefaultencoding()))
        logger.info('From ' + url + ' get the text success...')
        return str(html.content)


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
    # url_file = os.popen('curl {}'.format(url)).read()
    url_file = get_base_file(url)
    if 'mode:' in url_file:
        with open(YAML_PATH, "wb") as f:
            f.write(url_file.replace('127.0.0.1:9090', '0.0.0.0:9090'))
            f.close()
        write_url(url)
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
    try:
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
    except Exception as ex:
        logger.info('set_proxy Error:' + ex)


# 取消代理参数
def set_none_proxy():
    os.system('gsettings set org.gnome.system.proxy mode "none"')
    logger.info('Agent cleared')
