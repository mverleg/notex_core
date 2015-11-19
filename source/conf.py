
from collections import OrderedDict
from json import load, dumps
from logging import warning
from os import getenv
from os.path import join, dirname, realpath, abspath
from appdirs import user_config_dir


class Settings():
	"""
		Should behave like a settings module.
	"""
	CONFIG_PATH_ENV = 'NOTEX_CONFIG'

	def __init__(self):
		self.config = self.get_user_config()

	@classmethod
	def get_version(cls):
		"""
			The version of the compiler.
		"""
		with open(join(cls.get_base_dir(), 'dev', 'VERSION')) as fh:
			return fh.read()

	@classmethod
	def get_base_dir(cls):
		"""
			Get the base directory of notex_core.
		"""
		return dirname(cls.get_code_dir())

	@staticmethod
	def get_code_dir():
		"""
			Get the source directory of notex_core.
		"""
		return dirname(realpath(__file__))

	def get_user_config(self):
		config = self.get_defaults()
		config.update(self.load_user_config_file())
		return config

	def get_defaults(self):
		#todo: maybe hardcode defaults, it feels too changeable now...
		with open(join(self.get_code_dir(), 'notex_config_defaults.json'), 'r') as fh:
			defaults = load(fp=fh, object_pairs_hook=OrderedDict)
		try:
			defaults['package_sources']['default']['directory'] = user_config_dir('notex')
		except KeyError:
			raise Exception('default config file appears incomplete')
		return defaults

	def get_user_config_location(self):
		default_path = join(user_config_dir('notex'), 'notex_config.json')
		path = getenv(self.CONFIG_PATH_ENV, None)
		if path:
			try:
				with open(path, 'r'): pass
			except (IOError, FileNotFoundError) as err:
				warning('From the environment variable "{0:s}" the path to config "{1:s}" was found, but this could not be opened and "{2:s}" will be used instead. {3:s}'.format(self.CONFIG_PATH_ENV, path, default_path, str(err)))
				return default_path
			else:
				return path
		else:
			return default_path

	def load_user_config_file(self):
		path = self.get_user_config_location()
		try:
			with open(path, 'r') as fh:
				user_conf = load(fp=fh, object_pairs_hook=OrderedDict)
		except (IOError, FileNotFoundError) as err:
			warning('No user config found at "{0:s}" - you can use --make_conf to create one - {1:s}'.format(path, str(err)))
			user_conf = {'config_file': None}
		else:
			user_conf['config_file'] = path
		return user_conf

	def __getattr__(self, item):
		if item in self.config:
			return self.config[item]
		return super(Settings, self).__getattribute__(item)

	def get_config_string(self):
		return dumps(self.config, indent=4, sort_keys=False)


settings = Settings()


