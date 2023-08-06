from struct import pack
from setuptools import setup, find_packages

setup(
    name='Mensajes-ghuamanciza',
    version='6.0',
    description='Un paquete para saludar y despedir',    
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),    
    author='Coach Python',
    author_email='echarlie33@gmail.com',
    url='https://www.echarlie33.com',
    license_files=['LICENSE'],
    packages=find_packages(),
    scripts=[],
    test_suite='tests',
    install_requires=[paquete.strip()
                        for paquete in open("requirements.txt").readlines()],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Topic :: Utilities'
    ]
)
