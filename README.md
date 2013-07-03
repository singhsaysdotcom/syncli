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
------------
```pip install syncli```

OR

```git clone https://github.com/singhsaysdotcom/syncli.git ~/syncli```

```ln -sf ~/syncli/syncli/syncli.py /usr/local/bin/syncli```



Usage
-----

Basic syntax is
```syncli --host <hostname> <command>```

syncli handles authentication in one of two ways. You can either specify a username and password as command line options

```syncli --host <hostname> --username <username> --password <password> <command>```

OR

you can put them in a configuration file `~/.syncli.yaml` by default. The config file is a yaml file with the following structure.

```yaml
host:
  username: <username>
  password: <password>
```

Credentials provided as command line arguments override values from the configuration file, if both exist.

**IMPORTANT: ** Currently authentication sends your credentials over http in plain text, so this is not safe to use at all over a public network or the internet. syncli defaults to 'http' (DSM default), but you override it with `--proto=https`.


Currently Supported Operations
------------------------------
 + reboot : reboots the device

```bash
$ syncli --host xxxxx reboot
Done
```

 + shutdown : shuts down the device

```bash
$ syncli --host xxxxx shutdown
Done
```

+ stats : prints stats from the resource monitor.

```bash
$ syncli --host xxxxx stats
cpu: 0% loadavg: 119 115 114
mem: 7% of 1GB
```

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

 + list_packages : lists all packages installed via the Package Manager.

```bash
$ syncli --host xxxxx list_packages
Plex Media Server (stop)
DHCP Server (running)
CouchPotato Server (stop)
Python (running)
SABnzbd (stop)
SickBeard (stop)
```

 + available_packages : lists all packages available for installation.

```bash
$ syncli --host xxxxx available_packages
iTunes Server (1.1-2270)
VPN Server (1.1-2267)
Cloud Station (2.0-2402)
Time Backup (1.2-2278)
Surveillance Station (6.0-2636)
Mono (2.11.1-0004)
Syslog Server (2.1-2309)
...
```

 + start_package : start the named package.

```bash
$ syncli --host xxxxx --package 'Plex Media Server' start_package
Done
```

 + stop_package : stops the named package.

```bash
$ syncli --host xxxxx --package 'Plex Media Server' stop_package
Done
```
