# bits-pypi-template

BITS pypi package template

To start a new BITS pypi package, create a new repo based off of this template. Then:

1) Rename `bits/example` directory to `bits/<packagename>`
2) In `package.sh`, change `bits_example` to `bits_<packagename>`
3) In `bits/<packagename>/__init__.py`, change mentions of `Example` to `PackageName`
4) In `test.py`, change `bits.example` to `bits.<packagename>`
5) Also in `test.py`, change mentions of `Example` to `PackageName`
6) Run `./test.py` to make sure everything is working
