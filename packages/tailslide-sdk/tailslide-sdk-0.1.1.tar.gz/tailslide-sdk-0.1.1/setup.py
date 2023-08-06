from setuptools import setup

setup(
    name='tailslide-sdk',
    version='0.1.1',
    description='A example Python package',
    url='https://github.com/shuds13/pyexample',
    author='Steven Liou, Trent Cooper, Elaine Vuong, Jordan Eggers',
    author_email='tailslide.io.2205@gmail.com ',
    license='MIT',
    packages=['src/tailslide'],
    install_requires=[
        "nats-py >= 2.1.4",
        "redis >= 4.3.4"
    ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
