#!/bin/bash

apt -y install vim bash-completion wget
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |tee  /etc/apt/sources.list.d/pgdg.list

apt update
apt -y install postgresql-13 postgresql-client-13 gcc python3-dev libpq-dev python3-pip libcairo2-dev pkg-config expect

pip install -U pip wheel

pip install -r requirements.txt

systemctl status postgresql.service
/usr/bin/expect <<-EOD
	#https://stackoverflow.com/questions/41186459/simulate-key-press-in-bash
	#process we monitor
	spawn systemctl status postgresql@13-main.service
	expect "Started PostgreSQL Cluster 13-main."
	send "q\r"
EOD


systemctl is-enabled postgresql

