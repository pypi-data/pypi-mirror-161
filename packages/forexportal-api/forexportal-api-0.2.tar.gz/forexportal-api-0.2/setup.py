from setuptools import setup

with open("README.md", 'r', encoding = 'utf-8') as file:
    read_me_description = file.read()

setup(name='forexportal-api',
      version='0.2',
      description='Forex Portal API',
      packages=['forexportal'],
      author_email='me@biteof.space',
      long_description=read_me_description,
      long_description_content_type="text/markdown",
      url="https://github.com/btfspace/forexportal-api",
      zip_safe=False,
      install_requires=['requests', 'websocket', 'websocket-client'],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
)