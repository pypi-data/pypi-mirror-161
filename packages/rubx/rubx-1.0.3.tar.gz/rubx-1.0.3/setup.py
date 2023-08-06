#!/bin/python
from distutils.core import setup
readmy : str = ('''
# rubika client with python3 module RUBX
# rubika library !
# self for account
@creator_ryson -> telegram


installing :

pip install rubx --upgrade


exmaple run and usage


from rubx import rubx

auth : str = ''
robot = rubx.Bot('AppName', auth=auth)

guid : str = ''

def main():
    while True:
        try:
            robot.reportObject(user=guid, mode='spam')
            break

main()


the powered by me and a friend''')
descript : str = ('''
# rubx for rubika client

# run :


from rubx import rubx
auth : str = ''
robot = rubx.Bot('AppName', auth=auth)

guid : str = ''

while 1:
  try:
    robot.reportObgect(user=guid, mode='spam')
    break
  except:
    pass


Mr. root
''')
setup(
  name = 'rubx',
  packages = ['rubx'],
  version = '1.0.3',
  license='MIT', 
  description = descript,
  long_description=readmy,
  author = 'Saleh - mr root',
  author_email = 'creator.ryson@gmail.com',
  url = 'https://github.com/mester-root/rubx',
  download_url = 'https://github.com/mester-root/rubx',
  keywords = ["rubx","rubix","rubikax","rubika","bot","robot","library","rubikalib","rubikalibrary","rubika.ir","web.rubika.ir","m.rubika.ir"],
  package_data={"": ["LICENSE", "NOTICE"]},
  package_dir={"rubx": "rubx"},
  include_package_data=True,
  zip_safe=False,
  install_requires=[
          'requests',
          'pycryptodome==3.10.1',
          'urllib3',
          'tqdm',
          'pyfiglet'
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
  project_urls={
    "Documentation": "https://github.com/Mester-Root/rubx/blob/main/README.md",
    "Source": "https://github.com/mester-root/rubx",
    },
)