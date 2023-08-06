from distutils.core import setup

setup(
	name="metax_api",
	packages=['metax_api'],
	version='0.2',
	license='gpl-3.0',
	description='Pyhton3 api client for metax',
	author='Mikhayil Martirosyan',
	author_email='mikhayil.martirosyan@realschool.am',
	url='https://gitlab.com/mm_arm/metax.api',
	keywords=['Metax', 'Leviathan', 'Ehayq', 'EhayqLLC', 'Instigate', 'Metax.api'],
	install_requires=[
		"websocket-client==0.37.0",
		"requests"
	]
)

