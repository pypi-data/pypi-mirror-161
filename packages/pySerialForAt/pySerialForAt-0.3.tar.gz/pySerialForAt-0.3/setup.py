from setuptools import setup,find_packages

with open("README.md","r",encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='pySerialForAt',
      version='0.3',
      description='串口forAT',
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
      url='https://gitee.com/bc-y/py-serial-for-atp',
      author='bc-y,w-8',
      author_email='mdzzdyxc@163.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=True,
      install_requires=["pySerial"#3.5
      ],
     )
#python setup.py sdist bdist_wheel
#python -m twine upload dist/*