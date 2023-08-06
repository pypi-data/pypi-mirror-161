import setuptools


def readme():
    with open('README.md') as f:
        return f.read()


VERSION = '0.0.1'

setuptools.setup(
    name='sqltrans',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    version=VERSION,
    license='MIT',
    description='Sequence matcher with displacement detection.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    author='Mateusz Matelski',
    author_email='m.z.matelski@gmail.com',
    url='https://github.com/m-matelski/sqltrans',
    keywords=['sql', 'transform', 'translate'],
    install_requires=['msqlparse==0.4.3'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
)
