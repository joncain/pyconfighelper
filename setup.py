import setuptools

setuptools.setup(name='pyconfighelper',
                 version = '0.0.1',
                 description='Retrieve an encrypted JSON configuration file from Github and decrypt it.',
                 url='http://github.com/joncain/pyconfighelper',
                 author='Jon Cain',
                 author_email='jon@joncain.net',
                 license='Apache 2.0',
                 install_requires=[
                     'google-cloud-kms',
                     'cryptography',
                     'requests'
                 ],
                 python_requires='>=3.6')