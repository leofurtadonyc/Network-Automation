# Network-Automation
These are collections of small Python projects and script utilities designed for network automation. They encompass simple yet practical tasks and provide an avenue for learning and experimenting with network automation using Python.

You should consider exploring **NetProvisionCLI** and **ChatNOC** for your ISP organization. These projects combine and enhance various scripts and concepts from this repository, offering more robust and comprehensive features.

Please use it within a Python virtual environment to avoid interfering with your Python environment. You can create one using the '`python -m venv name_environment`' command, then activate it with '`source name_environment/bin/activate`'. Alternatively, you may use Pipenv, Poetry, Conda, or any other tool you choose. 

Easy steps (on a Mac computer):

1. `mkdir sandbox`
2. `cd sandbox`
3. `python3 -m venv network-automation-env`
4. `source network-automation-env/bin/activate`
5. `git clone https://github.com/leofurtadonyc/Network-Automation.git`
7. `pip install --upgrade pip` (if needed)
8. `pip install -r Network-Automation/requirements.txt`

On Windows:
1. Create the directory as shown above.
2. `python -m venv network-automation-env`
3. `.\network-automation-env\Scripts\activate`
4. `git clone https://github.com/leofurtadonyc/Network-Automation.git` (you may need Git. Tip: `winget install --id Git.Git -e --source winget`)
5. `pip install --upgrade pip` (if needed)
6. `pip install -r .\Network-Automation\requirements.txt`

While a _requirements.txt_ file for managing Python dependencies has been included, there may be issues depending on your operating system. Non-Python dependencies also exist, so please ensure BGPq3 or BGPq4 and Whois are installed if your computer doesn't already have them.

Check the [Wiki pages](https://github.com/leofurtadonyc/Network-Automation/wiki) for detailed instructions and use cases.

Please reach out to me with any suggestions, tips, code reviews, or other input you might have!
