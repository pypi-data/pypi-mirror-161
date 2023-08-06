import pkg_resources


path = pkg_resources.resource_filename('cndversion', 'VERSION')
__version__ = open(path).read()
