import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(name='alerting',
                 version='0.0.9.3',
                 author='Sina Rezaei',
                 author_email='sinarezaei1991@gmail.com',
                 long_description_content_type="text/markdown",
                 long_description=long_description,
                 description='Alerting: Easy to Use alerting library for Python',
                 url='https://github.com/sinarezaei/alerting',
                 license='MIT',
                 packages=setuptools.find_packages(),
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 install_requires=required,
                 python_requires='>=3.6',
                 zip_safe=False)
