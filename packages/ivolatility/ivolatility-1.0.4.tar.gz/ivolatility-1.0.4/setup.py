from setuptools import setup, find_packages

setup(
    name='ivolatility',
    version='1.0.4',
    description='IVolatility API wrapper package',
    url='https://github.com/shuds13/pyexample',
    author='Vladimir Goldin',
    author_email='vgoldin@egartech.ru',
    license='BSD 2-clause',
    packages=['ivolatility'],
    install_requires=['pandas',
                      'requests',
                      ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',  
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
