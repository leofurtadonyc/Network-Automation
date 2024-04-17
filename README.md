# Network-Automation
This is a set of Python script utilities designed for network automation. They encompass simple yet useful tasks, providing an avenue for learning and experimenting with network automation using Python.

To prevent interference with your Python environment, ensure that you use it within a Python virtual environment. You can create one using the '`python -m venv name_environment`' command, then activate it with '`source name_environment/bin/activate`'. Alternatively, you may use Pipenv, Poetry, Conda, or any other tool you choose. 

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

While a requirements.txt file for managing Python dependencies has been included, there may be issues depending on your operating system. Non-Python dependencies also exist, so ensure BGPq3 and Whois are installed if your computer doesn't already have them.

Check the Wiki pages for detailed instructions and use cases.

Feel free to reach out to me with any suggestions, tips, code reviews, or other input you might have!
