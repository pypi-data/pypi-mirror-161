from setuptools import setup,find_packages

with open("README.en.md","r",encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='pySerialForAt',
      version='0.1',
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
      zip_safe=True
     )
#python3 setup.py sdist bdist_wheel
#python3 -m twine upload dist/*