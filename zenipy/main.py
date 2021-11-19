#! /usr/bin/env python
# -*- coding:utf-8 -*-

import signal
import atexit
import config
import ssr2clash
import webbrowser

from gi.repository import Gtk
from gi.repository import AppIndicator3 as appindicator
from subprocess import Popen

APPINDICATOR_ID = 'ClashV'
LOGO_W = '/opt/ClashV/logo-w.svg'
LOGO_B = '/opt/ClashV/logo-b.svg'
switch = 0
indicator = appindicator.Indicator.new(APPINDICATOR_ID, LOGO_W, appindicator.IndicatorCategory.SYSTEM_SERVICES)
clashV = Popen(args='/opt/ClashV/clash', shell=True)


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(application_id="com.aim.clashV")

    def do_activate(self):
        if not hasattr(self, "clashV"):
            self.hold()
            self.my_app_settings = "Primary application instance."
            print(self.my_app_settings)
        else:
            print("Already running!")


def main():
    config.logger.info('Create a tray menu')
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    Gtk.main()


# This class reference to https://github.com/Baloneo/ssr-gtk
class SettingWindow(Gtk.Window):
    def on_ok_btn_clicked(self, widget):
        global clashV
        url = self.entry.get_text()
        config.logger.info('Ok button was clicked')
        self.label_msg.set_text("加载中...")
        if config.download_yaml(url):
            self.label_msg.set_text("加载失败")
        else:
            self.label_msg.set_text("加载成功")
        clashV.kill()
        clashV = Popen(args='/opt/ClashV/clash', shell=True)

    def on_link_btn_clicked(self, widget):
        global clashV
        url = self.entry.get_text()
        config.logger.info('Link button was clicked')
        if ssr2clash.link_to_clash(url):
            self.label_msg.set_text("转换失败")
        else:
            self.label_msg.set_text("添加成功")
        clashV.kill()
        clashV = Popen(args='/opt/ClashV/clash', shell=True)

    def __init__(self, *args, **kwargs):
        super(SettingWindow, self).__init__(*args, **kwargs)
        self.set_title("设置ClashV订阅信息")
        self.set_default_size(380, 50)
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)  # 垂直的盒子把水平占满

        self.entry = Gtk.Entry()
        old_url = config.read_url()
        self.entry.set_text(old_url or "设置clash订阅地址")
        self.vbox.pack_start(self.entry, False, False, 0)

        # 在一个水平的容器添加两个元素 vv_box 用来占用所有的左边空余空间 button使用剩下的必须空间大小
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # 显示信息栏
        self.label_msg = Gtk.Label("订阅存储在~/.config/clash/")
        # 允许用户从标签中选择文本进行复制和粘贴
        self.label_msg.set_selectable(True)
        hbox.pack_start(self.label_msg, True, True, 0)
        # 转链按钮
        self.button_ssr = Gtk.Button("链接转clash")
        self.button_ssr.connect("clicked", self.on_link_btn_clicked)
        hbox.pack_start(self.button_ssr, False, False, 0)
        # 下载按钮
        self.button_ok = Gtk.Button("确认")
        self.button_ok.connect("clicked", self.on_ok_btn_clicked)
        hbox.pack_start(self.button_ok, False, False, 0)

        self.vbox.pack_start(hbox, False, False, 0)
        # 将容器添加到窗口
        self.add(self.vbox)
        self.present()
        self.show_all()
        config.logger.info('Initialize the configuration window')


# 系统托盘
def build_menu():
    menu = Gtk.Menu()
    if switch == 0:
        item_agent_stop = Gtk.MenuItem('暂停代理')
        item_agent_stop.connect('activate', stop_agent)
        menu.append(item_agent_stop)
    else:
        item_agent_start = Gtk.MenuItem('继续代理')
        item_agent_start.connect('activate', start_agent)
        menu.append(item_agent_start)
    #
    item_conf = Gtk.MenuItem('配置')
    item_conf.connect('activate', clash_conf)
    menu.append(item_conf)
    item_console = Gtk.MenuItem('控制台')
    item_console.connect('activate', console)
    menu.append(item_console)
    item_quit = Gtk.MenuItem('退出')
    item_quit.connect('activate', clash_quit)
    menu.append(item_quit)
    menu.show_all()
    return menu


def stop_agent(source):
    global switch
    switch = 1
    indicator.set_menu(build_menu())
    config.set_none_proxy()


def start_agent(source):
    global switch
    switch = 0
    indicator.set_menu(build_menu())
    config.set_proxy()


def console(source):
    webbrowser.open("http://clash.razord.top/#/", new=0, autoraise=True)


def clash_conf(source):
    config.logger.info('Configure button was clicked')
    SettingWindow()


def clash_quit(source):
    config.logger.info('Exit button was clicked')
    clashV.kill()
    config.set_none_proxy()
    Gtk.main_quit()
    config.logger.info('Project exits')


@atexit.register
def _atexit():
    clashV.kill()


if __name__ == "__main__":
    pid = config.os.popen("ps -ef | grep '/opt/ClashV/zenipy/main.pyc' |grep -v grep |wc -l").read()
    if int(pid) <= 1:
        config.logger.info('Project starting')
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        config.set_proxy()
        main()
    else:
        config.logger.info('In the operation of the project')
