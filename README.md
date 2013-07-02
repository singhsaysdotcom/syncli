syncli
======

Python CLI for Synology DSM.


Dependencies
------------

 + Python 2.7 or greater
 + PyYaml
   + `pip install pyyaml` or `easy_install pyyaml`
 + requests
   + `pip install requests` or `easy_install requests`


Installation
----------
` git clone https://github.com/singhsaysdotcom/syncli.git ~/syncli`

` ln -sf ~/syncli/syncli.py /usr/local/bin/syncli`



Usage
-----

Basic syntax is
`syncli --host <hostname> <command>`

syncli handles authentication in one of two ways. You can either specify a username and password as command line options

`syncli --host <hostname> --username <username> --password <password> <command>`

OR

you can put them in a configuration file `~/.syncli.yaml` by default. The config file is a yaml file with the following structure.

```yml
host:
  username: <username>
  password: <password>
```

Credentials provided as command line arguments override values from the configuration file, if both exist.

**IMPORTANT: ** Currently authentication sends your credentials over http in plain text, so this is not safe to use at all over a public network or the internet. syncli defaults to 'http' (DSM default), but you override it with `--proto=https`.


Currently Supported Operations
------------------------------
 + info : prints out system information

```bash
$ syncli --host xxxxx info
ntpenabled : True
ramsize : 1024
usbdev : []
usbbaselevel : 1
ntpserver : ntp.xxxxxxx.xxx
satadev : []
timezone : Melbourne
version : DSM 4.2-3211
systemp : 34
systime : 2013-07-03 05:53:39
optime : 15:32:13
model : DS412+
serial : XXXXXXXXXX
systempwarn : False
```

 + list_packages:

```bash
$ syncli.py --host xxxxx list_packages
Plex Media Server (stop)
DHCP Server (running)
CouchPotato Server (stop)
Python (running)
SABnzbd (stop)
SickBeard (stop)
```

 + start_package

```bash
$ syncli.py --host xxxxx --package 'Plex Media Server' start_package
Done
```

 + stop_package

```bash
$ syncli.py --host xxxxx --package 'Plex Media Server' stop_package
Done
```
