
from collections import OrderedDict
from json import load, dumps
from os import getenv
from os.path import join, dirname, realpath, abspath
from appdirs import user_config_dir


class BaseSettings:
	"""
	This should be extended by specific setting classes (compiler, package manager, document...).
	They should be considered singletons (it's not enforced).
	"""
	_DEFAULT_VALUES_FILE = 'defaults.json'
	_CONFIG_PATH_DEFAULT = join(user_config_dir('notex'), 'default_config.json')
	_CONFIG_PATH_ENV = 'NOTEX_DEFAULT_CONFIG'

	def __init__(self):
		"""
		Set the default configuration values. Should be overridden by subclasses.
		"""
		self._code_dir = dirname(realpath(__file__))
		self._config = OrderedDict()

	def __getattr__(self, item):
		"""
		All public properties (not starting with _) are looked up in config dictionary.
		"""
		if not item.startswith('_'):
			try:
				return self._config[item]
			except KeyError:
				raise
		return super(BaseSettings, self).__getattr__(item)

	def __setattr__(self, item, value):
		"""
		All public properties (not starting with _) are stored in config dictionary.
		"""
		if not item.startswith('_'):
			self._config[item] = value
		super().__setattr__(item, value)

	def __repr__(self):
		return '{0:s}'.format(self.__class__.__name__)

	def __str__(self):
		return dumps(self._config, indent=4, sort_keys=False)

	#todo: custom json dump?
	#todo: hash?

	def _add_defaults(self):
		"""
		Set the defaults for all configuration options that have defaults.
		"""
		with open(join(self._code_dir, self._DEFAULT_VALUES_FILE), 'r') as fh:
			defaults = load(fp=fh, object_pairs_hook=OrderedDict)
		self._config.update(defaults)

	def _add_config_file(self):
		"""
		Update the configuration as specified by the user in a file, with defaults for unspecified values.
		"""
		path = self._get_user_config_location()
		try:
			with open(path, 'r') as fh:
				user_conf = load(fp=fh, object_pairs_hook=OrderedDict)
		except (IOError, FileNotFoundError) as err:
			user_conf = {'config_file': None}
		else:
			user_conf['config_file'] = path
		self._config.update(user_conf)

	def _add_packages(self):
		"""
		Update the configuration based on packages.
		"""
		#todo

	def _add_document_tags(self):
		"""
		Update the configuration based on configuration tags in the document.
		"""
		#todo

	def _add_cmd_arguments(self):
		"""
		Update the configuration based on command line options that have been provided.
		"""
		#todo

	def _get_user_config_location(self):
		"""
		Get the location that the user configuration is stored at.
		"""
		if getenv(self._CONFIG_PATH_ENV, None):
			path = abspath(getenv(self._CONFIG_PATH_ENV))
			if path:
				try:
					with open(path, 'r'):
						pass
				except (IOError, FileNotFoundError) as err:
					self.logger.warn(('From the environment variable "{0:s}" the path to config "{1:s}" was found, ' +
						'but this could not be opened and "{2:s}" will be used instead. Reason: {3:s}')
						.format(self._CONFIG_PATH_ENV, path, self._CONFIG_PATH_DEFAULT, str(err)))
					return self._CONFIG_PATH_DEFAULT
				else:
					return path
		return self._CONFIG_PATH_DEFAULT


class CompileSettings(BaseSettings):
	_DEFAULT_VALUES_FILE = 'compile_defaults.json'
	_CONFIG_PATH_DEFAULT = join(user_config_dir('notex'), 'compile_config.json')
	_CONFIG_PATH_ENV = 'NOTEX_COMPILE_CONFIG'

	def __init__(self):
		super(CompileSettings, self).__init__()
		self._add_defaults()
		self._add_config_file()
		self._add_packages()
		self._add_document_tags()
		self._add_cmd_arguments()


class DocumentSettings(BaseSettings):
	_DEFAULT_VALUES_FILE = 'compile_defaults.json'
	_CONFIG_PATH_DEFAULT = None
	_CONFIG_PATH_ENV = None

	def __init__(self):
		super(DocumentSettings, self).__init__()
		self._add_defaults()
		self._add_packages()
		self._add_document_tags()


