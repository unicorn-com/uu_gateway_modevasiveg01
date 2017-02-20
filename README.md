mod_evasive
===========

Fork of mod_evasive for Apache 2.x. Original module by Deep Logic, Inc

WHAT IS MOD_EVASIVE ?

mod_evasive is an evasive maneuvers module for Apache to provide evasive
action in the event of an HTTP DoS or DDoS attack or brute force attack.  It
is also designed to be a detection tool, and can be easily configured to talk
to ipchains, firewalls, routers, and etcetera.

Detection is performed by creating an internal dynamic hash table of IP
Addresses and URIs, and denying any single IP address from any of the following:

- Requesting the same page more than a few times per second
- Making more than 50 concurrent requests on the same child per second
- Making any requests while temporarily blacklisted (on a blocking list)

This method has worked well in both single-server script attacks as well
as distributed attacks, but just like other evasive tools, is only as
useful to the point of bandwidth and processor consumption (e.g. the
amount of bandwidth and processor required to receive/process/respond
to invalid requests), which is why it's a good idea to integrate this
with your firewalls and routers.

This module instantiates for each listener individually, and therefore has
a built-in cleanup mechanism and scaling capabilities.  Because of this,
legitimate requests are rarely ever compromised, only legitimate attacks.  Even
a user repeatedly clicking on 'reload' should not be affected unless they do
it maliciously.

One module is provided in this forked version:

Apache v2.x API:	mod_evasive2.c

HOW IT WORKS

A web hit request comes in. The following steps take place:

- The IP address of the requestor is looked up on the temporary blacklist
- The IP address of the requestor and the URI are both hashed into a "key".
  A lookup is performed in the listener's internal hash table to determine
  if the same host has requested this page more than once within the past
  1 second.
- The IP address of the requestor is hashed into a "key".
  A lookup is performed in the listerner's internal hash table to determine
  if the same host has requested more than 50 objects within the past
  second (from the same child).

If any of the above are true, a 403 response is sent.  This conserves
bandwidth and system resources in the event of a DoS attack.  Additionally,
a system command and/or an email notification can also be triggered to block
all the originating addresses of a DDoS attack.

Once a single 403 incident occurs, mod_evasive now blocks the entire IP
address for a period of 10 seconds (configurable).  If the host requests a
page within this period, it is forced to wait even longer.  Since this is
triggered from requesting the same URL multiple times per second, this
again does not affect legitimate users.

The blacklist can/should be configured to talk to your network's firewalls
and/or routers to push the attack out to the front lines, but this is not
required.

mod_evasive also performs syslog reporting using daemon.alert.  Messages
will look like this:

Aug  6 17:41:49 elijah mod_evasive[23184]: [ID 801097 daemon.alert] Blacklisting address x.x.x.x: possible attack.

WHAT IS THIS TOOL USEFUL FOR?

This tool is *excellent* at fending off request-based DoS attacks or scripted
attacks, and brute force attacks. When integrated with firewalls or IP filters,
mod_evasive can stand up to even large attacks. Its features will prevent you
from wasting bandwidth or having a few thousand CGI scripts running as a
result of an attack.

If you do not have an infrastructure capable of fending off any other types
of DoS attacks, chances are this tool will only help you to the point of
your total bandwidth or server capacity for sending 403's.  Without a solid
infrastructure and address filtering tool in place, a heavy distributed DoS
will most likely still take you offline.


CHANGES OVER STOCK
------------------
Apache 2.4 and 2.0 modules are consolidated to 1 module, mod_evasive. Prior 
to this change modules were referenced as mod_evasive20 and mod_evasive24. 
Second, the activation threshold has changed from a cooldown rate to absolute
frequency. In the original mod_evasive release, DOS[Page,Site]Interval set the expiry
rate between requests. So long as another request happened before DOS[Page,Site]Interval
expired, it would be possible to increment the bean counter. For polling apps,
this is disastrous. An app that polled once a second for 10 seconds is just as guilty
as a client polling 10 times in 1 second. This altered release takes the remote client, 
sets the timestamp, then blocks if [page,site] count exceeds DOS[Page,Site]Count within 
DOS[Page,Site]Interval seconds.

A simple fail2ban recipe is bundled with this release to transform short-term
403 responses into long-term iptables blocking. Use with care, but works well for
brute-force deterrents.

HOW TO INSTALL

FAIL2BAN
--------
fail2ban provides an agent to watch for abusive clients that trigger the
mod_evasive threshold and temporarily block via iptables instead of
sending a 403 response. With recidive jail support, repeat offenders can be
permanently blocked thus reducing wasted CPU clock cycles.

FAIL2BAN INSTALLATION
---------------------
Copy the optional apache-modevasive.conf to fail2ban filter storage, 
typically /etc/fail2ban/filter.d.

Activate the jail by adding the following to jail.conf:


>[evasive]
enabled = true
filter = apache-modevasive
action = iptables-multiport[name=evasive, port="http,https", proto=tcp]
logpath = %(syslog_daemon)s
maxretry = 1
findtime = 120
bantime = 120
ignoreip = 127.0.0.1

Then reload fail2ban: `fail2ban-client reload`. It's also recommended to
activate recidive support to ban long-term abusers.

APACHE v2.x
-----------

1. Extract this archive

2. Run $APACHE_ROOT/bin/apxs -i -a -c mod_evasive2.c

3. The module will be built and installed into $APACHE_ROOT/modules, and loaded into your httpd.conf

4. Restart Apache

CONFIGURATION APACHE v2.x
-----------
<IfModule mod_evasive.c>
    DOSHashTableSize    3097
    DOSPageCount        2
    DOSSiteCount        50
    DOSPageInterval     1
    DOSSiteInterval     1
    DOSBlockingPeriod   10
</IfModule>


You will also need to add this line if you are building with dynamic support:

APACHE v2.4
-----------

LoadModule evasive_module modules/mod_evasive.so

(This line is already added to your configuration by apxs)

DOSHashTableSize
----------------

The hash table size defines the number of top-level nodes for each child's
hash table.  Increasing this number will provide faster performance by
decreasing the number of iterations required to get to the record, but
consume more memory for table space.  You should increase this if you have
a busy web server.  The value you specify will automatically be tiered up to
the next prime number in the primes list (see mod_evasive.c for a list
of primes used).

DOSPageCount
------------

This is the threshhold for the number of requests for the same page (or URI)
per page interval.  Once the threshhold for that interval has been exceeded,
the IP address of the client will be added to the blocking list.

DOSSiteCount
------------

This is the threshhold for the total number of requests for any object by
the same client on the same listener per site interval.  Once the threshhold
for that interval has been exceeded, the IP address of the client will be added
to the blocking list.

DOSPageInterval
---------------

The interval for the page count threshhold; defaults to 1 second intervals.

DOSSiteInterval
---------------

The interval for the site count threshhold; defaults to 1 second intervals.

DOSBlockingPeriod
-----------------

The blocking period is the amount of time (in seconds) that a client will be
blocked for if they are added to the blocking list.  During this time, all
subsequent requests from the client will result in a 403 (Forbidden) and
the timer being reset (e.g. another 10 seconds).  Since the timer is reset
for every subsequent request, it is not necessary to have a long blocking
period; in the event of a DoS attack, this timer will keep getting reset.

DOSEmailNotify
--------------

If this value is set, an email will be sent to the address specified
whenever an IP address becomes blacklisted.  A locking mechanism using /tmp
prevents continuous emails from being sent.

NOTE: Be sure MAILER is set correctly in mod_evasive.c.
      The default is "/bin/mail -t %s" where %s is
      used to denote the destination email address set in the configuration.
      If you are running on linux or some other operating system with a
      different type of mailer, you'll need to change this.

DOSSystemCommand
----------------

If this value is set, the system command specified will be executed
whenever an IP address becomes blacklisted.  This is designed to enable
system calls to ip filter or other tools.  A locking mechanism using /tmp
prevents continuous system calls.  Use %s to denote the IP address of the
blacklisted IP.

DOSLogDir
---------

Choose an alternative temp directory

By default "/tmp" will be used for locking mechanism, which opens some
security issues if your system is open to shell users.

  	http://security.lss.hr/index.php?page=details&ID=LSS-2005-01-01

In the event you have nonprivileged shell users, you'll want to create a
directory writable only to the user Apache is running as (usually apache, 
see "User" directive in httpd.conf) then set this in your httpd.conf.

WHITELISTING IP ADDRESSES

IP addresses of trusted clients can be whitelisted to insure they are never
denied.  The purpose of whitelisting is to protect software, scripts, local
searchbots, or other automated tools from being denied for requesting large
amounts of data from the server.  Whitelisting should *not* be used to add
customer lists or anything of the sort, as this will open the server to abuse.
This module is very difficult to trigger without performing some type of
malicious attack, and for that reason it is more appropriate to allow the
module to decide on its own whether or not an individual customer should be
blocked.

To whitelist an address (or range) add an entry to the Apache configuration
in the following fashion:

DOSWhitelist	127.0.0.1
DOSWhitelist	127.0.0.*

Wildcards can be used on up to the last 3 octets if necessary.  Multiple
DOSWhitelist commands may be used in the configuration.

TWEAKING APACHE

The keep-alive settings for your children should be reasonable enough to
keep each child up long enough to resist a DOS attack (or at least part of
one).  Remember, it is the child processes that maintain their own internal
IP address tables, and so when one exits, so does all of the IP information it
had. For every child that exits, another 5-10 copies of the page may get
through before putting the attacker back into '403 Land'.  With this said,
you should have a very high MaxRequestsPerChild, but not unlimited as this
will prevent cleanup.

You'll want to have a MaxRequestsPerChild set to a non-zero value, as
DosEvasive cleans up its internal hashes only on exit.  The default
MaxRequestsPerChild is usually 10000.  This should suffice in only allowing
a few requests per 10000 per child through in the event of an attack (although
if you use DOSSystemCommand to firewall the IP address, a hole will no
longer be open in between child cycles).

TESTING

Want to make sure it's working? Run test.pl, and view the response codes.
It's best to run it several times on the same machine as the web server until
you get 403 Forbidden messages. Some larger servers with high child counts
may require more of a beating than smaller servers before blacklisting
addresses.

Please don't use this script to DoS others without their permission.

KNOWN BUGS

- This module appears to conflict with the Microsoft Frontpage Extensions.
  Frontpage sucks anyway, so if you're using Frontpage I assume you're asking
  for problems, and not really interested in conserving server resources anyway.

FEEDBACK

Please feel free to fork and fix issues or open new ones.

Original author: jonathan@nuclearelephant.com
Modified package: matt@apisnetworks.com


