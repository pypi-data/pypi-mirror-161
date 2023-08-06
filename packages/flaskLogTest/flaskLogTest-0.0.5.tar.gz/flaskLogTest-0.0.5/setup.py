from setuptools import find_packages, setup
setup(
    name='flaskLogTest',#the name of the package when installing
    packages=find_packages(include=['beansofts']), #include the folder which contain the functions
    version='0.0.5', #the version   realease
    description='this is a simple flasklogger v=0.0.4', 
    readme="README.md",
    author='Me', 
    license='MIT',
    install_requires=['pika','flask','geocoder','PyJWT==1.7.1'], #list of requirement modules used
    setup_requires=['pytest-runner'], 
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)
