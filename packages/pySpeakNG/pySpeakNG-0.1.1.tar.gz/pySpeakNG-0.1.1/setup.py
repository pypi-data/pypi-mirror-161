from pathlib import Path

from setuptools import setup, find_packages

HERE = Path(__file__).parent.resolve()

d = 'A thin wrapper around eSpeak-NG for off-line text-to-speech synthesis.'
long_description = (HERE/'README.md').read_text(encoding='utf-8')

setup(
    name='pySpeakNG',
    version='0.1.1',
    author='David E. Lambert',
    author_email='david@davidelambert.com',
    description=d,
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/davidelambert/pyspeakng',
    project_urls={
        'Bug Reporting': 'https://github.com/davidelambert/pyspeakng/issues',
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Operating System :: POSIX :: Linux',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    python_requires='>=3.10',
    package_data={
        'pySpeakNG': ['*.json', ]
    }
)
