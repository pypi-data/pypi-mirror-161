import setuptools
from scode import __version__ as scode_version

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="scode", # Replace with your own username
    version=scode_version,
    author="강동욱, 선준우, 강진영, 박태준, 김도현, 임성현",
    maintainer = '강동욱',
    maintainer_email="ehddnrwork@gmail.com",
    description="The Private Package of Showm Company.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/showm-dev/Standard",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.6',
    install_requires=[
        'selenium==3.141.0',
        'paramiko',
        'dropbox',
        'telegram',
        'python-dateutil',
        'requests',
        'pyperclip',
        'chromedriver-autoinstaller',
        'fake-useragent',
        'anticaptchaofficial',
        'python_anticaptcha',
        'feedparser',
    ],
)
