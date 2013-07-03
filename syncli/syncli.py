#!/usr/bin/env python
"""Command Line Interface for Synology DSM."""

import argparse
import logging
import os
import requests
import sys
import time
import yaml

# default values.
DEFAULTS = {
  'port': 5000,
  'proto': 'http'
}

# module uris.
LOGIN = '/login.cgi'
LOGOUT = '/ logout.cgi'
REBOOT = '/  reboot.cgi'
SYSTEMINFO = '/modules/SystemInfoApp/SystemInfo.cgi'
PKGMAN = '/modules/PkgManApp/PkgMan.cgi'
PKGSYNOMAN = '/modules/PkgManApp/PkgSynoMan.cgi'
RESOURCEMONITOR = '/modules/ResourceMonitor/rsrcmonitor2.cgi'

# all available commands.
COMMANDS = []


def command(func):
  """Decorator to register a fn as an available command."""
  if func.__name__ not in COMMANDS:
    COMMANDS.append(func.__name__)
  return func


def humanize(number, suffix=''):
  """Transforms given input into human readable format."""
  if number > 1e9:
    return '%dG%s' % (round(number/1e9, 1), suffix)
  if number > 1e6:
    return '%dM%s' % (round(number/1e6, 1), suffix)
  if number > 1e3:
    return '%dK%s' % (round(number/1e3, 1), suffix)
  return '%d%s' % (number, suffix)



class SynoBox(object):
  """Represents a Synology Device."""

  def __init__(self, host, port=DEFAULTS['port'], proto=DEFAULTS['proto'],
               config_file=None):
    self.host = host
    self.port = port
    self.proto = proto
    self.username = None
    self.password = None
    self.session_id = None
    self.cookies = None
    if config_file is not None:
      self.read_config(host, config_file)
    self.base_url = '%(proto)s://%(host)s:%(port)s/webman' % self.config()

  def __enter__(self):
    if self.session_id is None:
      self.login()
    return self

  def __exit__(self, typ, value, traceback):
    return self.logout()

  def read_config(self, host, config_file):
    """Read configuration from a configuration file."""
    if os.path.exists(config_file):
      logging.debug('Reading configuration from %s', config_file)
      with open(config_file, 'r') as f:
        config = yaml.safe_load(f.read())
        if host not in config:
          logging.debug('Host %s not found in config file', config_file)
          return False
        else:
          for k in ['proto', 'port', 'username', 'password']:
            if k in config[host]:
              setattr(self, k, config[host][k])
    else:
      logging.debug('Config file %s doesn\'t exist or not readable',
                    config_file)

  def config(self):
    """Returns configuration as a dict."""
    return {
        'host': self.host,
        'port': self.port,
        'proto': self.proto,
        'username': self.username,
        'password': self.password
    }

  def login(self):
    """Login and store session cookies."""
    if self.session_id is None:
      logging.debug('Authenticating ...')
      url = self.base_url + LOGIN
      data = {'username': self.username, 'passwd': self.password}
      resp = requests.post(url, data)
      if resp.status_code == 200:
        self.session_id = resp.cookies['id']
        self.cookies = resp.cookies

  def logout(self):
    """Logout and cleanup existing session."""
    url = self.base_url + LOGOUT
    resp = requests.get(url, cookies=self.cookies, allow_redirects=False)
    if resp.status_code == 302:
      self.cookies = None
      self.session_id = None
      logging.debug('Logged out ...')
      return True
    return False

  def _get(self, uri, data=None, method='POST'):
    """Fetch a url from this device with proper authentication cookies."""
    url = self.base_url + uri
    logging.debug('Fetching %s', url)
    resp = None
    if method == 'POST':
      resp = requests.post(url, data, cookies=self.cookies)
    else:
      resp = requests.get(url, cookies=self.cookies)
    logging.debug(resp.status_code)
    logging.debug(resp.text)
    return resp.json()

  @command
  def info(self, _):
    """Prints device information."""
    uri = SYSTEMINFO
    data = {'_dc': int(time.time() * 1e3), 'query': 'overview'}
    resp = self._get(uri, data)
    for k, v in resp.iteritems():
      print('%s : %s' % (k, v))

  @command
  def list_package_sources(self, _):
    """Lists all registered packages sources/repositories."""
    uri = PKGSYNOMAN
    data = {'action': 'listfeed'}
    resp = self._get(uri, data)
    for src in resp['items']:
      print '%(name)s (%(feed)s)' % src

  def all_packages(self):
    """Fetch a list of all known packages."""
    uri = PKGSYNOMAN
    data = {'action': 'list'}
    data_other = {'action': 'listother'}
    pkg_data = self._get(uri, data)
    pkg_data_other = self._get(uri, data_other)
    return pkg_data['data'] + pkg_data_other['data']

  @command
  def list_packages(self, _):
    """Lists pacakges installed via Package Manager."""
    for d in self.all_packages():
      if 'pkgstatus' in d:
        print '%(dname)s (%(version)s)  -- %(pkgstatus)s' % d

  @command
  def available_packages(self, _):
    """Lists packages available for installation via Package Manager."""
    for d in self.all_packages():
      if 'pkgstatus' not in d:
        print '%(dname)s (%(version)s)' % d

  @command
  def start_package(self, args):
    """Starts a package installed via Package Manager."""
    uri = PKGMAN
    data = {'action': 'apply',
            'operation': 'start',
            'packagename': args.package}
    resp = self._get(uri, data)
    if resp['success']:
      print 'Done'
    else:
      print('Failed to start package %s', args.pacakge)

  @command
  def stop_package(self, args):
    """Stops a packagei installed via Package Manager."""
    uri = PKGMAN
    data = {'action': 'apply',
            'operation': 'stop',
            'packagename': args.package}
    resp = self._get(uri, data)
    if resp['success']:
      print 'Done'
    else:
      print('Failed to start package %s', args.pacakge)

  @command
  def stats(self, _):
    """Prints resource usage stats."""
    uri = RESOURCEMONITOR
    data = {'action': 'system_load_widget'}
    resp = self._get(uri, data)
    if 'cpu' in resp:
      print('cpu: %(SystemLoad)s%% loadavg: %(1minLoad)s %(5minLoad)s '
            '%(15minLoad)s' % resp['cpu'])
    if 'memory' in resp:
      print('mem: %(RealUsage)s%%' % resp['memory']),
      print('of %s' % humanize(resp['memory']['RamSize'] * 1e3, suffix='B'))

  def reboot_or_shutdown(self, opt='reboot'):
    """Reboot or shutdown the device."""
    uri = REBOOT
    data = {'_dc': int(time.time() * 1e3), 'opt': opt}
    resp = self._get(uri, data)
    if resp['success']:
      print 'Done'
    else:
      print('Failed to %s device.' % opt)

  @command
  def reboot(self, _):
    """Reboot the device."""
    self.reboot_or_shutdown()

  @command
  def shutdown(self, _):
    """Shutdown the device."""
    self.reboot_or_shutdown(opt='shutdown')


def main():
  """Instantiates a SynoBox and runs commands against it."""
  parser = argparse.ArgumentParser(description="Synology DSM CLI")
  # TODO(singhsays): convert this to subparsers for each command.
  parser.add_argument('command',  choices=COMMANDS)
  parser.add_argument('--package', default=None, help='package name')
  parser.add_argument('--host', help='hostname or IP address.',
                      required=True)
  parser.add_argument('--port', help='port',
                      default=DEFAULTS['port'])
  parser.add_argument('--proto', help='protocol',
                      default=DEFAULTS['proto'], choices=['http', 'https'])
  parser.add_argument('--username', help='DSM username')
  parser.add_argument('--password', help='DSM password')
  parser.add_argument('--config_file', help='configuration file',
                      default='~/.syncli.yaml')
  parser.add_argument('--loglevel', help='logging level', default='error',
                      choices=['debug', 'info', 'warning', 'error', 'critical'])
  args = parser.parse_args()
  logging.basicConfig(level=getattr(logging, args.loglevel.upper()))
  config_file = os.path.expanduser(os.path.expandvars(args.config_file))
  config_file_ok = (os.path.exists(config_file) and
                    os.access(config_file, os.R_OK))
  if not config_file_ok and not (args.username and args.password):
    print 'must provide readable config file or authentication credentials.'
    parser.print_help()
    sys.exit(2)
  if args.username and args.password:
    logging.debug('Using authentication credentails from arguments.')
    with SynoBox(args.host, args.port) as d:
      d.username = args.username
      d.password = args.password
      getattr(d, args.command)(args)
  else:
    logging.debug('Using configuration file %s', args.config_file)
    with SynoBox(args.host, config_file=config_file) as d:
      getattr(d, args.command)(args)


if __name__ == '__main__':
  main()
