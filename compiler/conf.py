
from collections import OrderedDict
from json import load, dumps
from os import getenv
from os.path import join, dirname, realpath
from appdirs import user_config_dir
from compiler.log import BasicLogger


class Settings:
	"""
	Should behave like a settings module.
	"""
	CONFIG_PATH_ENV = 'NOTEX_CONFIG'

	def __init__(self):
		self._config = self._get_config()
		# self._config['verbosity'] = float('inf')
		# self._logger = None

	def __getattr__(self, item):
		# if item != 'config' and item in self._config:
		# 	return self._config[item]
		# return self.__getattribute__(item)
		if not item.startswith('_'):
			return self._config[item]
		return super().__getattr__(item)
		#self.__getattribute__(item)

	def __setattr__(self, item, value):
		if not item.startswith('_'):
			self._config[item] = value
		super().__setattr__(item, value)

	@classmethod
	def _get_base_dir(cls):
		"""
			Get the base directory of notex_core.
		"""
		return dirname(cls._get_code_dir())

	@staticmethod
	def _get_code_dir():
		"""
			Get the source directory of notex_core.
		"""
		return dirname(realpath(__file__))

	def _get_config(self):
		"""
		Get the configuration as specified by the user, with defaults for unspecified values.
		"""
		config = self._get_defaults()
		config.update(self._load_user_config_file())
		return config

	def _get_defaults(self):
		"""
		Get the defaults for configuration options.
		"""
		#todo: maybe hardcode defaults, it feels too changeable now, and may give parser errors...
		with open(join(self._get_code_dir(), 'notex_config_defaults.json'), 'r') as fh:
			defaults = load(fp=fh, object_pairs_hook=OrderedDict)
		try:
			defaults['package_sources']['default']['directory'] = user_config_dir('notex')
		except KeyError:
			raise Exception('default config file appears incomplete')
		return defaults

	def _get_user_config_location(self):
		"""
		Get the location that the user configuration is stored at.
		:return:
		"""
		standard_path = join(user_config_dir('notex'), 'notex_config.json')
		path = getenv(self.CONFIG_PATH_ENV, None)
		if path:
			try:
				with open(path, 'r'):
					pass
			except (IOError, FileNotFoundError) as err:
				self.logger.warn(('From the environment variable "{0:s}" the path to config "{1:s}" was found, ' +
					'but this could not be opened and "{2:s}" will be used instead. Reason: {3:s}')
					.format(self.CONFIG_PATH_ENV, path, standard_path, str(err)))
				return standard_path
			else:
				return path
		else:
			return standard_path

	def _load_user_config_file(self):
		"""
		Load the configuration file set by the user.
		"""
		path = self._get_user_config_location()
		try:
			with open(path, 'r') as fh:
				user_conf = load(fp=fh, object_pairs_hook=OrderedDict)
		except (IOError, FileNotFoundError) as err:
			# warning('No user config found at "{0:s}" - you can use make_conf to create one (message: {1:s})'
			# 	.format(path, ']'.join(str(err).split(']')[1:])))
			user_conf = {'config_file': None}
		else:
			user_conf['config_file'] = path
		return user_conf

	def get_config_string(self):
		return dumps(self._config, indent=4, sort_keys=False)

	# @property
	# def logger(self):
	# 	if self._logger is None:
	# 		self._logger = BasicLogger()
	# 	return self._logger
	#
	# @logger.setter
	# def logger(self, value):
	# 	self._logger = value


