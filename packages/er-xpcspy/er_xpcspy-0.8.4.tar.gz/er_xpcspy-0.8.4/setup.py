from setuptools import setup, find_packages
import os

from xpcspy.__init__ import __version__


cwd = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(cwd, 'requirements.txt'), 'r') as f:
    requirements = f.readlines()

package_name = os.environ.get('PYPI_NAME') or 'xpcspy'
package_repo = os.environ.get('PYPI_URL') or 'https://github.com/hot3eed/xpcspy'

print(package_name)

setup(
    name=package_name,
    description="XPC message interception and more",
    license='Apache-2.0',
    author='hot3eed',
    author_email='hot3eed@gmail.com',
    url=package_repo,
    keywords=['macos', 'ios', 'xnu', 'xpc', 'frida'],
    version=__version__,
    packages=find_packages(),
    install_requires=requirements,
    package_data={
        'xpcspy': [os.path.join(cwd, './_agent.js')]
        },
    entry_points={
        'console_scripts': [
                f'xpcspy={package_name}.console.cli:main'
            ]
        }
)

