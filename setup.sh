#!/bin/bash
installFun(){
	hash `yum list installed |grep libappindicator-gtk3` >/dev/null 2>&1 &
	if [ "$?" != "0" ]; then
		yum install -y gir1.2-appindicator3-0.1
	fi
	PY_VERSION=`python -V 2>&1|awk '{print $2}'|awk -F '.' '{print $1}'`
	hash pip >/dev/null 2>&1 &
	if [ "$?" != "0" ]; then
		python ./get-pip$PY_VERSION.py
	fi
	pip show pyyaml >/dev/null 2>&1 &
	if [ "$?" != "0" ]; then
		if (( $PY_VERSION == 3 )); then
	    pip install pyyaml
		elif (( $PY_VERSION == 2 )); then
	  pip install PyYAML
		fi
	fi

	pip show zenipy >/dev/null 2>&1 &
	if [ "$?" != "0" ]; then
	  pip install zenipy
	fi

	mkdir -p ~/.config/clash
	mkdir -p /opt/ClashV/zenipy
	
	cp ./clash /opt/ClashV
	cp ./config.yaml ~/.config/clash
	cp ./Country.mmdb ~/.config/clash
	python -m py_compile ./zenipy/*.py
	mv ./zenipy/*.pyc /opt/ClashV/zenipy
	cp ./clashv.png /opt/ClashV/logo.png
	cp ./logo-w.svg /opt/ClashV/logo-w.svg
	cp ./logo-b.svg /opt/ClashV/logo-b.svg
	cp ./ClashV.desktop /usr/share/applications/ClashV.desktop

	chmod +x /opt/ClashV/clash

	echo "success"
}

unInstallFun(){
	ps -ef |grep clash |grep '/ClashV' |grep -v grep |awk '{print $2}' |xargs kill -9 >/dev/null 2>&1 &

	rm -r ~/.config/clash/

	sudo rm -r /opt/ClashV/
	sudo rm /usr/share/applications/ClashV.desktop

	ps -ef |grep defunct |grep -v grep |awk '{print $3}' |xargs kill -9 >/dev/null 2>&1 &

	echo "success"
}

case "$1" in
ins)
    installFun
    ;;
unins)
    unInstallFun
    ;;    
*)
    echo "ins|unins"
    ;;
esac