import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requires = f.read().splitlines()

setuptools.setup(
    name='ondewo-sip-client',
    version='3.5.0',
    author='Ondewo GbmH',
    author_email='info@ondewo.com',
    description='provides endpoints and messages for gRPC communication with the ONDEWO SIP server',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ondewo/ondewo-sip-client-python',
    packages=[
        np
        for np in filter(
            lambda n: n.startswith('ondewo.') or n == 'ondewo',
            setuptools.find_packages()
        )
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Libraries',
    ],
    python_requires='>=2.7, !=3.0.1',
    install_requires=requires,
)
