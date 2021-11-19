#! /usr/bin/env python
# -*- coding:utf-8 -*-
#############################################
#  将订阅转为Clash
#############################################
import re
import json
import base64
import config


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
            links = config.get_base_file(url)
            if re.match('^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{4}|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)$', links):
                all_links = base64_decode(links)
                config.logger.info('From the encoded text decoding success...')
                return all_links
            else:
                yaml_data = config.yaml.load(links, Loader=config.yaml.RoundTripLoader)
                nodes = []
                for i, value in enumerate(yaml_data['proxies']):
                    nodes.append(yaml_data['proxies'][i])
                return nodes
        except Exception as ex:
            config.logger.info('getAllLinks Error:' + ex)


# 从ssr链接中得到节点信息 如参数不对应在此调整
def get_node_ssr(node):
    try:
        info = base64_decode(node)
        ssr_dict = json.loads(info)
        node_info = {
            'name': str(ssr_dict['remarks'] or ssr_dict['name']),
            'server': str(ssr_dict['server']),
            'port': int(ssr_dict['port'] or ssr_dict['server_port']),
            'type': 'ssr',
            'password': str(ssr_dict['password'] or ssr_dict['pwd']),
            'cipher': str(ssr_dict['method']),
            'protocol': str(ssr_dict['protocol']),
            'obfs': str(ssr_dict['obfs'])

        }
        return node_info
    except Exception as ex:
        config.logger.info('getNodeSsr Error:', ex)


def get_node_vmess(node):
    try:
        info = base64_decode(node)
        vmess_dict = json.loads(info)
        node_info = {
            'name': str(vmess_dict['ps']),
            'server': str(vmess_dict['add']),
            'port': int(vmess_dict['port']),
            'type': 'vmess',
            'uuid': str(vmess_dict['id']),
            'alterId': str(vmess_dict['aid']),
            'cipher': 'auto',
            'network': str(vmess_dict['net']),
            'ws-path': str(vmess_dict['path']),
            'skip-cert-verify': True,
            'tls': True
        }
        return node_info
    except Exception as ex:
        config.logger.info('getNodeVmess Error:', ex)


# 从订阅链接得到所有节点信息
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
        elif 'vmess://' in all_links:
            links = all_links.split('vmess://')
            for vmess in links:
                if vmess:
                    node = get_node_vmess(vmess)
                    all_nodes.append(node)
        else:
            all_nodes = all_links
    except Exception as ex:
        config.logger.info('getAllNodes Error: {}'.format(ex))
    else:
        config.logger.info('For all the nodes information successfully...')
        return all_nodes


# 写文件
def write_clash_file(nodes):
    try:
        config.logger.info(nodes)
        with open(config.YAML_PATH, 'r+') as f:
            yaml_data = config.yaml.load(f, Loader=config.yaml.RoundTripLoader)
            proxies_info = yaml_data['proxies']
            if proxies_info is None:
                proxies_info = []
            # 开始遍历链接
            for dict_info in nodes:
                proxies_info.append(dict_info)
                if yaml_data.has_key('proxy-groups'):
                    for pg in yaml_data['proxy-groups']:
                        if pg['name'] == '全局代理':
                            continue
                        pg_proxies = pg['proxies']
                        if pg_proxies is None:
                            pg_proxies = []
                        # 多个连接名称追加
                        pg_proxies.append(str(dict_info['name']))
                        # 设置选择名称
                        pg['proxies'] = pg_proxies
            # 设置新的链接
            yaml_data['proxies'] = proxies_info
            f.seek(0)
            f.truncate()
            config.yaml.dump(data=yaml_data, stream=f, Dumper=config.yaml.RoundTripDumper, allow_unicode=True,
                             default_flow_style=False)
    except Exception as ex:
        config.logger.info('Write to file failed, Exception:{}'.format(ex))
        return 1
    else:
        config.logger.info('Written to the file to complete.')
        return None


# 通过网络链接/ssr/vmess将转成clash
def link_to_clash(url):
    if '://' not in url:
        url = 'https://free886.herokuapp.com/clash/proxies?type=ssr'
    nodes = get_all_nodes(url)
    return write_clash_file(nodes)
