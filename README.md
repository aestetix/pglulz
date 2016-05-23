This is a fun little script that will generate a custom gpg key and proceed to
auto-sign all matching keys that exist in a keyserver.

To install (in virtualenv):
apt-get install python-dev libyaml-dev python-virtualenv
git clone $this_repo
cd $this_repo
virtualenv .
source bin/activate
pip install -r requirements.txt

Make any changes you need to pglulz.yaml, and then run
python pglulz.py

And watch lulz happen. If you want to run it in "real_run" mode, make sure to
set that option to "True" in the yaml config file.

Do be warned that anything you run in "real_run" mode will make irrevocable
changes to the keyserver you run against.
