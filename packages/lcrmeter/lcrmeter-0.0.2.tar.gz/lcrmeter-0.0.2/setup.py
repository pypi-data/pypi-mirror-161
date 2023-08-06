from setuptools import setup, find_packages

# The text of the README file
with open("README.md", encoding="utf-8") as f:
    README = f.read()

setup(
    name='lcrmeter',
    version='0.0.2',
    license='MIT',
    author="César J. Lockhart de la Rosa",
    author_email='lockhart@imec.be',
    description="API for the Keysight E4980A LCR Meter",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={'': 'src'},
    url='https://github.imec.be/lockhart/lcrmeter',
    keywords='LCR Meter, impedance, api, keysight, E4980A',
    install_requires=[],

)