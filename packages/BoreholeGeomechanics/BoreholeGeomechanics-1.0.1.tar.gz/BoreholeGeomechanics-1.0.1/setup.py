from setuptools import setup

def readme():
    with open('README.md') as f:
        README =f.read()
    return README
    
setup(
    name="BoreholeGeomechanics",
    version="1.0.1",
    description="BoreholeGeomechanics",
    long_description=readme(),
    long_description_content_type='text/markdown',
    #url='https://github.com/...',
    author="Mai Linh Doan & Lahcene Bellounis",
    licence='GPL-3.0',
    classifiers=[
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Programming Language :: Python :: 3" ,
    "Programming Language :: Python :: 3.8",
    ],
#    packages=['BoreholeGeomechanics'],
    py_modules=['BoreholeGeomechanics'],
    include_package_data=True,
    install_requires=["pandas","matplotlib","numpy"],

    )
    
    
