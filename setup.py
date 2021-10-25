from setuptools import setup, find_packages


setup(name='pythonequipmentdrivers',
      version='1.10.0',
      description="""
                  A library of software drivers to interface with various
                  pieces of test instrumentation
                  """,
      url='https://github.com/AnnaGiasson/PythonEquipmentDrivers',
      author='Anna Giasson',
      author_email='AnnaGraceGiasson@GMail.com', license='MIT',
      packages=find_packages(), zip_safe=False,
      classifiers=[
                   'Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python'
                   ],
      install_requires=[
                        'pyvisa',
                        'numpy',
                        'pypiwin32',
                        ],
      )
