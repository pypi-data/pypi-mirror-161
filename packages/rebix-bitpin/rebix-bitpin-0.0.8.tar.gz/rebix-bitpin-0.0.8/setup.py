from distutils.core import setup

setup(
    name='rebix-bitpin',
    packages=['rebix_bitpin'],
    version='0.0.8',
    license='MIT',
    description='Bitpin cryptocurrency exchange python sdk',
    author='rebix',
    author_email='cnashohrat@gmail.com',
    url='https://github.com/Rebix/rebix-bitpin',
    keywords=['bitpin', 'crypto', 'exchange', 'API', "SDK"],
    install_requires=[
        'requests',
        'simplejson',
        'nice-tools',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
