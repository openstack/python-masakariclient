============
Installation
============

**Note:** The paths we are using for configuration files in these steps
are with reference to Ubuntu Operating System. The paths may vary for
other Operating Systems.

The branch_name which is used in commands, specify the branch_name
as stable/<branch> for any stable branch installation. For eg:
stable/queens, stable/pike. If unspecified the default will be
master branch.

Using python install
====================
Clone and install python-masakariclient repository.::

    $ cd ~/
    $ git clone https://github.com/openstack/python-masakariclient -b <branch_name>
    $ cd python-masakariclient
    $ sudo python setup.py install


Using pip
=========

You can also install the latest version by using ``pip`` command:::

    $ pip install python-masakariclient


Or, if it is needed to install ``python-masakariclient`` from master branch,
type::

    $ pip install git+https://github.com/openstack/python-masakariclient.git

