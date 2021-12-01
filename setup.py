# to test locally:
# python setup.py develop
#
# to deploy:
# rm -rf ./dist
# python setup.py sdist bdist_wheel
# python -m twine upload --repository pypi dist/*
#
# more info here:
# https://packaging.python.org/tutorials/packaging-projects/#uploading-your-project-to-pypi

import setuptools

setuptools.setup(name = 'get_cover_art',
    version = '1.4.12',
    python_requires = '>=3.5',
    author = 'Rego Sen',
    author_email = 'regosen@gmail.com',
    url = 'https://github.com/regosen/get_cover_art',
    description = 'Batch cover art downloader and embedder for audio files',
    long_description = open("README.md","r").read(),
    long_description_content_type = "text/markdown",
    license = 'MIT',
    keywords = 'cover album art artwork embed itunes apple music mp3 id3 m4a mp4 aac xmp flac ogg vorbis opus songs',
    packages = setuptools.find_packages(),
    install_requires = [
        'mutagen',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    entry_points = {
        'console_scripts': [
            'get_cover_art = get_cover_art.__main__:main',
        ]
    },
)