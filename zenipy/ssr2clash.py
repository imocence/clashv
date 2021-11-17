#! /usr/bin/env python
# -*- coding:utf-8 -*-
#############################################
#  将SSR订阅转为ClashR
#############################################
import os
import re
import base64
import codecs
import logback
import requests

logger = logback.Logger()
HOME = os.getenv("HOME")
YAML_PATH = os.path.join(HOME, ".config/clash/config.yaml")


# 获取链接文本
def get_base_file(url):
    try:
        html = requests.get(url)
        html.raise_for_status
        html.encoding = html.apparent_encoding
    except IOError as ioe:
        logger.info('getBasefile Error:', ioe)
    else:
        logger.info('From ' + url + ' get the text success...')
        return str(html.text)


# base64解码
def base64_decode(base64_encode_str):
    need_padding = len(base64_encode_str) % 4

    if need_padding != 0:
        missing_padding = 4 - need_padding
        base64_encode_str += '=' * missing_padding

    return base64.urlsafe_b64decode(base64_encode_str).decode('utf-8')


# 从加密文本解码出所有ssr链接
def get_all_links(url):
    if 'http' not in url:
        return url
    else:
        try:
            links = get_base_file(url)
            if re.match('^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$', links):
                all_links = base64_decode(links)
                logger.info('From the encoded text decoding success...')
                return all_links
            else:
                return links
        except Exception as ex:
            logger.info('getAllLinks Error:' + ex)


# 从ssr链接中得到节点信息 如参数不对应在此调整
def get_node_ssr(node):
    try:
        node_info = {}
        info = base64_decode(node)
        front_val = info.split('/?')[0]
        node_info['server'] = front_val.split(':')[0]
        node_info['port'] = front_val.split(':')[1]
        node_info['protocol'] = front_val.split(':')[2]
        node_info['method'] = front_val.split(':')[3]
        node_info['obfs'] = front_val.split(':')[4]
        node_info['pwd'] = base64_decode(front_val.split(':')[5])

        rear_val = info.split('/?')[1]
        for a in rear_val.split('&'):
            b = a.split('=')[0]
            c = base64_decode(a.split('=')[1])
            node_info[b] = c

        # print(node_info)
        return node_info

    except Exception as ex:
        logger.info('getNodeR Error:', ex)


# 设置SSR节点
def set_nodes(nodes):
    proxies = []
    for node in nodes:
        name = node['remarks'] or node['name']
        server = node['server']
        port = node['port']
        cipher = node['method'] or node['cipher']
        pwd = node['pwd'] or node['password']
        protocol = node['protocol']
        obfs = node['obfs']

        if 'group' in node:
            group = node['group']
        else:
            group = ''

        if 'protoparam' in node:
            proparam = node['protoparam']
        else:
            proparam = ''

        if 'obfsparam' in node:
            obparam = node['obfsparam']
        else:
            obparam = ''

        proxy = '- { name: ' + '\"' + str(name).strip() + '\"' + ', type: ssr, server: ' + '\"' + str(
            server) + '\"' + ', port: ' + str(
            port) + ', password: ' + '\"' + str(pwd) + '\"' + ', cipher: ' + '\"' + str(
            cipher) + '\"' + ', protocol: ' + '\"' + str(
            protocol) + '\"' + ', protocolparam: ' + '\"' + str(proparam) + '\"' + ', obfs: ' + '\"' + str(
            obfs) + '\"' + ', obfsparam: ' + '\"' + str(obparam) + '\"' + ' }\n'
        proxies.append(proxy)
    proxies.insert(0, '\nProxy:\n\n')
    return proxies


# 设置策略组
def set_proxy_group(nodes):
    proxy_names = ''
    for node in nodes:
        proxy_names = proxy_names + '\"' + (node['remarks'] or node['name']) + '\",'

    proxy_names = str(proxy_names[:-1])
    g_url = 'http://www.gstatic.com/generate_204'
    proxy_0 = '- { name: "总模式", type: select, proxies: ' + ' [\"手动切换\",\"延迟最低\",\"负载均衡\",\"故障切换\",\"DIRECT\"] }\n'
    proxy_1 = '- { name: "手动切换", type: select, proxies: [' + proxy_names + '] }\n'
    proxy_2 = '- { name: "延迟最低", type: url-test, proxies: [' + proxy_names + '], url: "' + g_url + '", interval: 300 }\n'
    proxy_3 = '- { name: "故障切换", type: fallback, proxies: [' + proxy_names + '], url: "' + g_url + '", interval: 300 }\n'
    proxy_4 = '- { name: "负载均衡", type: load-balance, proxies: [' + proxy_names + '], url: "' + g_url + '", interval: 300 }\n'

    apple = '- { name: "Apple服务", type: select, proxies: ' + ' [\"DIRECT\",\"手动切换\",' + proxy_names + '] }\n'
    global_media = '- { name: "国际媒体", type: select, proxies: ' + ' [\"手动切换\",' + proxy_names + '] }\n'
    china_media = '- { name: "中国媒体", type: select, proxies: ' + ' [\"DIRECT\"] }\n'
    reject_web = '- { name: "屏蔽网站", type: select, proxies: ' + ' [\"REJECT\",\"DIRECT\"] }' + '\n\n\n\n\n\n'

    rule = "# 规则\n"

    proxy_group = ['\nProxy Group:\n\n', proxy_0, proxy_1, proxy_2, proxy_3, proxy_4, apple, global_media, china_media,
                   reject_web, rule]
    return proxy_group


# 从ssr链接汇总得到所有节点信息
def get_all_nodes(url):
    try:
        all_nodes = []
        all_links = get_all_links(url)
        if 'ssr://' in all_links:
            links = all_links.split('ssr://')
            for ssr in links:
                if ssr:
                    node = get_node_ssr(ssr.replace('\n', ''))
                    all_nodes.append(node)
        else:
            return all_links
    except Exception as ex:
        logger.info('getAllNodes Error: {}'.format(ex))
    else:
        logger.info('For all the nodes information successfully...')
        return all_nodes


# 写文件
def write_clash_file(nodes):
    try:
        logger.info(nodes)
        if '- {"' in nodes:
            info = nodes
        else:
            info = set_nodes(nodes) + set_proxy_group(nodes)

        with codecs.open(YAML_PATH, "a", encoding='utf-8') as f:
            f.write(' \n\n')
            if 'proxies' not in info:
                f.write('proxies:\n')
            f.writelines(info)
            f.closed
    except Exception as ex:
        logger.info('Write to file failed, the reason:{}'.format(ex))
        return 1
    else:
        logger.info('Written to the file to complete.')
        return None


# 通过网络链接将ssr转成clash
def ssr_to_clash(url):
    if 'http' not in url:
        url = 'https://free886.herokuapp.com/clash/proxies?type=ssr'
    nodes = get_all_nodes(url)

    return write_clash_file(nodes)
