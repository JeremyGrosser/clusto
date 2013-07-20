##################################
  Getting Started
##################################

:Release: |version|
:Date: |today|

Installation
------------

From debian package
~~~~~~~~~~~~~~~~~~~
Add the following to /etc/apt/sources.list.d/clusto.list::

 deb http://ppa.launchpad.net/synack/clusto/ubuntu precise main
 deb-src http://ppa.launchpad.net/synack/clusto/ubuntu precise main

Update the index and install clusto::

 # aptitude update
 # aptitude install clusto

Building an rpm package
~~~~~~~~~~~~~~~~~~~~~~~
You may need to install rpmdevtools beforehand, or run the rpmbuild as root::

 $ cd rpm/
 $ ./make_tarball.sh
 $ rpmbuild -ta clusto-$VERSION.tar.gz

From source
~~~~~~~~~~~
::

 $ git clone git://github.com/clusto/clusto.git
 $ cd clusto
 $ python setup.py build

As root::

 # python setup.py install
 # mkdir /etc/clusto /var/lib/clusto
 # cp conf/* /etc/clusto/
 # cp contrib/* /var/lib/clusto/

Required dependencies
~~~~~~~~~~~~~~~~~~~~~

- Python 2.6 or later (not compatible with Python 3)
- SQLAlchemy: http://www.sqlalchemy.org/
- IPython: http://ipython.scipy.org/moin/
- IPy: http://c0re.23.nu/c0de/IPy/

Optional dependencies
~~~~~~~~~~~~~~~~~~~~~

- webob: http://webob.org/
  required for clusto-httpd
- scapy: http://www.secdev.org/projects/scapy/
  required for clusto-dhcpd and clusto-snmptrapd for packet construction and decoding
- paramiko: https://github.com/paramiko/paramiko
  required for clusto-update-info
- simplejson: http://code.google.com/p/simplejson/
  makes clusto-httpd and related clients faster
- python-memcache: http://www.tummy.com/software/python-memcached/
  enables caching with the memcached option in clusto.conf to improve performance

Quick Start
-----------

/etc/clusto/clusto.conf::

 [clusto]
 dsn = sqlite:////var/lib/clusto/clusto.db

More information on DSN strings and use of alternative databases is available in the SQLAlchemy documentation http://docs.sqlalchemy.org/en/rel_0_7/core/engines.html. Clusto has been used in production environments with SQLite, PostgreSQL, MySQL, and MariaDB. Other databases supported by SQLAlchemy may work, but success is not guaranteed.


::

 $ clusto-initdb

Congratulations, you should now have a clusto database with a working schema and a single "ClustoMeta" entity (which stores information about things like schema version and should generally be ignored). Now you can start creating objects and populating the database. Clusto's CLI tools cover the day-to-day actions you may want to perform, but more rare things like adding a new datacenter need to be done through clusto-shell, which essentially spawns ipython with the clusto environment configured. Let's create a datacenter with a rack and a couple servers by importing some "Drivers" and creating "Entities" from them. Each entity has a name that must be unique within a global namespace. For example, you cannot have two servers with the same name. These names generally map to hostnames for convenience, but they can be whatever you like. Try to avoid encoding too much information into names, as you can't query on pieces of a name.

clusto-shell::

 > from clusto.drivers import BasicDatacenter, BasicRack, BasicServer
 > dc = BasicDatacenter('sfo1')
 > rack = BasicRack('sfo1-r0001')
 > dc.insert(rack)
 > server1 = BasicServer('s0001')
 > server2 = BasicServer('s0002')
 > rack.insert(server1, 1)
 > rack.insert(server2, 2)

You'll notice that we added an extra argument to the insert() method for the rack. This is because the BasicRack driver enforces a constraint that all servers must be associated with a RU, which is an integer 1-45. If your racks have a different number of RU available, you will need to subclass BasicRack by writing a Clusto plugin. For now, let's assume that BasicRack is fine. Now we'll setup an IPManager for the subnets we manage. IPManager is an instance of a Clusto ResourceManager, which allows you to track and manage the allocation of arbitrary resources; in this case, IP addresses.

::

 > from clusto.drivers import IPManager
 > ipm = IPManager(baseip='10.0.0.0', netmask='255.255.255.0', gateway='10.0.0.254')
 > ipm.allocate(server1)
 > server2.bind_ip_to_osport('10.0.0.2', 'eth0')

Here, we've created an IPManager entity with a few options to tell Clusto what IP space this manager will be responsible for. The gateway argument is entirely optional, but is handy if you want to use Clusto to generate network configs later. This code snippet demonstrates two different ways of attaching an IP to a server. The first method, using allocate(), tells the IPManager to pick the next available IP address and associate it with the server1 entity. The second method, bind_ip_to_osport() is a convenience method on IPMixin (a superclass of BasicServer that gives any Driver object IP functionality) that associates a pre-defined IP address with the given interface on a server. Note that bind_ip_to_osport did not require a reference to the IPManager entity. bind_ip_to_osport first queries the database to determine which IPManager entity is managing the given IP address, then performs the allocation. This method will throw an exception if an IP is specified that is not within a subnet managed by a Clusto IPManager.
