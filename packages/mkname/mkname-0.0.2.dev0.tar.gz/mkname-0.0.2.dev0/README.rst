######
mkname
######

A Python package for building names by using other names as building
blocks.


Why?
====
It started with an update to a blackjack game I wrote as my first
project in Python. I wanted to have a bunch of computer players
playing with you, and thought they should be randomly generated
with randomly generated names. Then it came up in a few other things
I wrote, so I figured I'd turn it into a package.


What does it do?
================
It pulls random names from a database, and can modify those names
before returning them. Major features include:

*   Use parts of multiple names to construct a new name.
*   Modify the selected or constructed names.
*   Use a default database of names.
*   Use your own database of names.
*   Import into your Python code as a package.
*   Use from the command line.


How do I run it?
================
To run the code:

1.  Clone the repository to your local system.
2.  Install the dependencies listed in `requirements.txt`
3.  Navigate to the root of the repository in your shell.
4.  Run the following command: `python -m mkname`

It should also be able to be imported into your Python code as a package.


How do I run the tests?
=======================
If you just want to run the unit tests:

    python -m unittest discover tests

If you're wanting a range of additional checks, including type and style
checks, run:

    ./precommit.py

Note: `precommit.py` requires itself to be run from a virtual environment
located in the `.venv` directory at the root of the repository. This is so
I don't accidentally run it using my system's Python and then waste hours
troubleshooting that mess. If you want to disable this, you'll have to
modify the script. The easiest way is probably commenting out the
`check_venv()` call in `main()`.
