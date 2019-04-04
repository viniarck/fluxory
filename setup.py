from setuptools import setup
from fluxory.__version__ import version
desc = 'Asynchronous high-performance distributed OpenFlow 1.3/1.5 framework'

setup(
    name='fluxory',
    version=version,
    description=desc,
    author='Vinicius Arcanjo',
    author_email='viniarck@gmail.com',
    keywords='OpenFlow SDN async asyncio distributed',
    url='http://github.com/viniarck/fluxory',
    python_requires='>3.7',
    packages=['fluxory'],
    license='Apache',
    install_requires=['nose>=1.3.7', 'pytest>=4.3.0', 'aio-pika>=5.2.3', 'netaddr>=0.7.19'],
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    zip_safe=False,
)
