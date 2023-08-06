Python package to create report for Frigel machines

# Table of Contents
1. [Project information](README.md#project-information)
2. [Package creation](README.md#package-creation)
3. [Installation on embedded systems](README#installation-on-embedded-systems)
3. [Usage](README.md#usage)
4. [Licensing](LICENSE.txt)

# Project information
This tool converts PEMS TCP to PEMS serial

# Package creation
How to create python package and upload it to [pypi](https://pypi.org/)
<pre><code>
pip install --upgrade twine
python setup.py sdist
python setup.py bdist_wheel
python setup.py build
python setup.py install
twine upload --repository pypi dist/*
</code></pre>

# Installation on embedded systems
If pip is not installed (ARM systems), first execute the following command
<pre><code>
python3 -m ensurepip --default-pip
</code></pre>

Then run the following commands for py-serial and pyserial-asyncio packages
<pre><code>
python3 setup.py install
</code></pre>

# Usage
Check [runs_server.py](#runs_server.py)