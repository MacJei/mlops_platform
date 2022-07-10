# Configuration file for jupyterhub.
import dockerspawner, os, pwd, shutil, sys
from jupyterhub.utils import random_port
from jupyterhub.auth import PAMAuthenticator
from tornado import gen
from tornado.concurrent import run_on_executor
from subprocess import Popen, PIPE

from tornado.httpclient import AsyncHTTPClient

try:
    import pamela
except Exception as e:
    pamela = None
    _pamela_error = e


class KDBAuthenticator(PAMAuthenticator):

	def kinit(self, data):
		user = data['username']
		self.log.info('Authenticating: ' + user)
		pwrd = data['password']

		realm = 'YANDEX.RU' # заменить на свой REALM
		kinit = '/usr/bin/kinit'
		krbcc = '/tmp/krb5cc_%s' % (user,) # This path is on the shared volume
		kuser = '%s@%s' % (user, realm)
		
		if os.path.exists(krbcc) and os.path.isdir(krbcc):
			shutil.rmtree(krbcc)
		
		kinit_args = [kinit, kuser, '-c', krbcc]
		pecho_args = ['echo', '-n', pwrd]
		self.log.info('Running: ' + ' '.join(kinit_args))
		
		pecho = Popen(pecho_args, stdout=PIPE)
		kinit = Popen(kinit_args, stdin=pecho.stdout, stdout=PIPE, stderr=PIPE)
		
		outs, errs = kinit.communicate()
		
		if len(errs.decode("utf-8")) == 0:
			self.log.info("Kinit success: %s", ' '.join(kinit_args))
			return user
		else:
			self.log.warning("Kinit failed %s %s %s", ' '.join(kinit_args), outs, errs)
		
	
	@run_on_executor
	def authenticate(self, handler, data):
		username = data['username']
		try:
			pamela.authenticate(username, data['password'], service=self.service, encoding=self.encoding)
		except pamela.PAMError as e:
			if handler is not None:
				self.log.warning("PAM Authentication failed (%s@%s): %s", username, handler.request.remote_ip, e)
			else:
				self.log.warning("PAM Authentication failed: %s", e)
		else:
			
			
			if not self.check_account:
				kinituser = self.kinit(data)
				return kinituser
			try:
				pamela.check_account(username, service=self.service, encoding=self.encoding)
			except pamela.PAMError as e:
				if handler is not None:
					self.log.warning("PAM Account Check failed (%s@%s): %s", username, handler.request.remote_ip, e)
				else:
					self.log.warning("PAM Account Check failed: %s", e)
			else:
				kinituser = self.kinit(data)
				return kinituser


c.JupyterHub.authenticator_class = KDBAuthenticator

#  If any errors are encountered when opening/closing PAM sessions, this is
#  automatically set to False.
c.PAMAuthenticator.open_sessions = False

# Configure JupyterHub to use the curl backend for making HTTP requests,
# rather than the pure-python implementations. The default one starts
# being too slow to make a large number of requests to the proxy API
# at the rate required.
AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

# Do not shut down user pods when hub is restarted
c.JupyterHub.cleanup_servers = False

# Check that the proxy has routes appropriately setup
c.JupyterHub.last_activity_interval = 60

# Don't wait at all before redirecting a spawning user to the progress page
c.JupyterHub.tornado_settings = {
    "slow_spawn_timeout": 0,
}

c.DockerSpawner.args = [f'--NotebookApp.allow_origin="*"']
c.JupyterHub.tornado_settings = {
    'headers': {
        'Access-Control-Allow-Origin': "*",
    },
}
c.DockerSpawner.args = [f'--NotebookApp.ip="0.0.0.0"']
c.DockerSpawner.args = [f'--NotebookApp.allow_remote_access=True']
c.DockerSpawner.args = [f'--NotebookApp.open_browser=False']
c.DockerSpawner.args = [f'--LabApp.open_browser=False']

#SSL certificates for https
c.JupyterHub.ssl_key = '/etc/jupyterhub/ssl/private.key'
c.JupyterHub.ssl_cert = '/etc/jupyterhub/ssl/private.cer'

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

# Spawn containers from this image
c.DockerSpawner.image_whitelist = {'base_image': 'base_image:latest',
	'user_image_1': 'user_image_1:latest',
	'user_image_2': 'user_image_2:latest',
	'user_image_3': 'user_image_3:latest',
	'user_image_4': 'user_image_4:latest',
	'user_image_5': 'user_image_5:latest'
	}
c.DockerSpawner.container_prefix='base_image'

c.JupyterHub.port = 8000
c.ConfigurableHTTPProxy.api_url = 'http://DNS:9001'

# Proxy config
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_port = 8081
# Should be set to a token for authenticating communication with the proxy
c.ConfigurableHTTPProxy.auth_token = "CONFIGPROXY_AUTH_TOKEN"

# Config the docker containers to find the hub
network_name = "host"
c.DockerSpawner.hub_ip_connect = '172.17.0.1'
c.DockerSpawner.use_internal_ip = False
c.DockerSpawner.network_name = network_name
# Pass the network name as argument to spawned containers
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }

c.DockerSpawner.volumes = {
	'/home/{safe_username}/work': {'bind': '/home/{safe_username}', 'mode': 'Z'}, 
	'/shared/jupyterhub': {'bind': '/shared/jupyterhub', 'mode': 'Z'}, 
	'/etc/krb5.conf': {'bind': '/etc/krb5.conf', 'mode': 'ro'},
	'/var/lib/sss/pubconf/krb5.include.d': {'bind': '/var/lib/sss/pubconf/krb5.include.d', 'mode': 'ro'},
	'/etc/alternatives/hadoop': {'bind': '/etc/alternatives/hadoop', 'mode': 'ro'},
	'/etc/alternatives/hadoop-conf': {'bind': '/etc/alternatives/hadoop-conf', 'mode': 'ro'},
	'/etc/alternatives/hadoop-fuse-dfs': {'bind': '/etc/alternatives/hadoop-fuse-dfs', 'mode': 'ro'},
	'/etc/alternatives/hadoop-httpfs-conf': {'bind': '/etc/alternatives/hadoop-httpfs-conf', 'mode': 'ro'},
	'/etc/alternatives/hadoop-kms-conf': {'bind': '/etc/alternatives/hadoop-kms-conf', 'mode': 'ro'},
	'/etc/alternatives/java': {'bind': '/etc/alternatives/java', 'mode': 'ro'},
	'/etc/alternatives/hive': {'bind': '/etc/alternatives/hive', 'mode': 'ro'},
	'/etc/alternatives/spark-conf': {'bind': '/etc/alternatives/spark-conf', 'mode': 'ro'},
	'/etc/alternatives/spark-shell': {'bind': '/etc/alternatives/spark-shell', 'mode': 'ro'},
	'/etc/alternatives/spark-submit': {'bind': '/etc/alternatives/spark-submit', 'mode': 'ro'},
	'/etc/hadoop': {'bind': '/etc/hadoop', 'mode': 'ro'},
	'/etc/hive': {'bind': '/etc/hive', 'mode': 'ro'},
	'/etc/spark': {'bind': '/etc/spark', 'mode': 'ro'},
	'/path/to/cloudera': {'bind': '/path/to/cloudera', 'mode': 'ro'}, # ваши пути к директории cloudera
	'/path/to/oracle': {'bind': '/path/to/oracle', 'mode': 'ro'}, # драйвера для работы с oracle ojdbc8.jar
	'/usr/lib/oracle/21/client64/lib': {'bind': '/usr/lib/oracle/21/client64/lib', 'mode': 'ro'},
}

c.DockerSpawner.environment = {'LD_LIBRARY_PATH': '/path/to/cloudera/parcels/CDH/lib64:/path/to/cloudera/parcels/CDH/lib64/debug:/path/to/cloudera/parcels/CDH/lib/hadoop/lib/native:/path/to/cloudera/parcels/CDH/lib/hbase/lib/native:/path/to/cloudera/parcels/CDH/lib/impala/lib:/path/to/cloudera/parcels/CDH/lib/impala/lib/openssl:/path/to/cloudera/parcels/CDH/lib/impala/sbin-debug:/path/to/cloudera/parcels/CDH/lib/impala/sbin-retail:/path/to/cloudera/parcels/CDH/lib/impala-shell/lib/thrift/protocol:/usr/lib/oracle/21/client64/lib',
}

c.DockerSpawner.extra_create_kwargs = {'user': 'root'}
# Root access
c.DockerSpawner.environment = {
  'GRANT_SUDO': '1',
  'UID': '0', 
}

# Remove containers once they are stopped
c.DockerSpawner.remove_containers = True

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

c.Authenticator.admin_users = {'admin_login'}
c.JupyterHub.admin_access = True

# JupyterLab default
c.Spawner.default_url = '/lab'

def prespawn_hook(spawner):
	username = spawner.user.name
	# Uncomment when use auto kinit
	krb5cc = '/tmp/krb5cc_' + username
	spawner.volumes[krb5cc] = {'bind': '/tmp/krb5cc_1000', 'mode': 'Z'}
	uid = pwd.getpwnam(username).pw_uid
	volume_path = os.path.join('/home/',username)
	volume_path = volume_path + '/work'
	if not os.path.exists(volume_path):
		oldmask = os.umask(000)
		os.mkdir(volume_path, 0o777)
		os.chown(volume_path, 1000, uid)

c.DockerSpawner.pre_spawn_hook = prespawn_hook


