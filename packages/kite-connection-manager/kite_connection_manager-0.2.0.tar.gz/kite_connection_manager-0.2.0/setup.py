from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='kite_connection_manager',
    packages=find_packages(),
    version='0.2.0',
    description='Manage Kite Connections',
    author='Shashwat Rastogi',
    author_email='shashwat1991@gmail.com',
    license='MIT',
    install_requires=['pyotp~=2.6.0', 'kiteconnect~=4.1.0', 'selenium~=4.3.0', 'websockets', 'requests',
                      'beautifulsoup4', 'six', 'webdriver-manager'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
    long_description=long_description,
    url="https://github.com/shashwat7/KiteConnectionManager",
)
