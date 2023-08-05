import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt') as fr:
    requirements = fr.read().splitlines()

setuptools.setup(
    name='optodetools',
    version='0.1',
    license='The MIT License (MIT)',
    author='Christopher Gordon',
    author_email='chris.gordon@dfo-mpo.gc.ca',
    description='A python library for simulating and correcting oxygen optode time response error',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cgrdn/optodetools',
    packages=setuptools.find_packages(),
    package_dir={'optodetools': 'optodetools'},
    install_requires=requirements,
    data_files=[],
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha'
    ],
    python_requires='>=3.4',
)