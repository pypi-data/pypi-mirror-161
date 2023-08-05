from setuptools import setup, find_packages

setup(
    name='vipro_python',
    version='0.1',
    license='MIT',
    author="Tom Medhurst",
    author_email='tom.medhurst@vigilantapps.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/underpinning/vipro-python',
    keywords='vipro jupyter jupyterlab notebook pika amqp convenience',
    install_requires=[
      'pika',
    ],
)