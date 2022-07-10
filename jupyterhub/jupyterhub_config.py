# Configuration file for jupyterhub.
import dockerspawner, os, pwd, shutil, sys
from jupyterhub.utils import random_port
from jupyterhub.auth import PAMAuthenticator
from tornado import gen
from tornado.concurrent import run_on_executor
from subprocess import Popen, PIPE

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

		realm = 'OPEN.RU'
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

# Config the docker containers to find the hub
network_name = "host"
c.DockerSpawner.hub_ip_connect = '172.17.0.1'
c.DockerSpawner.use_internal_ip = False
c.DockerSpawner.network_name = network_name
# Pass the network name as argument to spawned containers
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }

# Explicitly set notebook directory because we'll be mounting a host volume to
# it.  Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
username = '{safe_username}'

c.DockerSpawner.volumes = {
	'/home/{safe_username}/work': {'bind': notebook_dir, 'mode': 'Z'}, 
	'/shared/jupyterhub': {'bind': '/shared/jupyterhub', 'mode': 'Z'}, 
	'/etc/krb5.conf': {'bind': '/etc/krb5.conf', 'mode': 'ro'},
	'/var/lib/sss/pubconf/krb5.include.d': {'bind': '/var/lib/sss/pubconf/krb5.include.d', 'mode': 'ro'},
	'/etc/alternatives/hadoop-conf': {'bind': '/etc/alternatives/hadoop-conf', 'mode': 'ro'},
	'/etc/alternatives/hive': {'bind': '/etc/alternatives/hive', 'mode': 'ro'},
	'/etc/alternatives/spark-conf': {'bind': '/etc/alternatives/spark-conf', 'mode': 'ro'},
	'/etc/hadoop': {'bind': '/etc/hadoop', 'mode': 'ro'},
	'/etc/hive': {'bind': '/etc/hive', 'mode': 'ro'},
	'/etc/spark': {'bind': '/etc/spark', 'mode': 'ro'},
	'/path/to/cloudera/etc': {'bind': '/path/to/cloudera/etc', 'mode': 'ro'},
	'/path/to/cloudera/parcel-cache': {'bind': '/path/to/cloudera/parcel-cache', 'mode': 'ro'},
	'/path/to/cloudera/parcels': {'bind': '/path/to/cloudera/parcels', 'mode': 'ro'},
	'/path/to/cloudera/security': {'bind': '/path/to/cloudera/security', 'mode': 'ro'},
}

# Remove containers once they are stopped
c.DockerSpawner.remove_containers = True

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

c.Authenticator.admin_users = {'admin_login'}

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


