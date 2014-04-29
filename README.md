maildelay
=========

Delay mails and deliver them according to a set of rules. More flexibility,
less disturbance.

Why
---

We all get too much mail, don't we? If you are subscribed to some
high-traffic mailing-lists (and/or you have many mail accounts) you know
the problem that you get mail every few minutes and it distracts you
from your actual work.

Current solution: Check mails N-times a day, otherwise ignore them. Hm,
but there are mails (from your mom) that require immediate action! What
we really want is much more flexibility! Wouldn't it be nice if we could
specify rules like:

- If I am at work, make sure that I get mails from the high-traffic box
at most every 2 hours. Send them accumulated, but between these bursts I
want silence from that box.
- I want silence during my work hours, but otherwise deliver the
high-traffic mails immediatly (because in my spare time I have nothing
else to do anyway).
- Deliver mails from box "foo" at 9:00 and 15:00 o'clock, otherwise shut
up.

Solution
--------
- Old setup:
```
getmail/fetchmail -> procmail -> maildir/boxes -> imapd/client
```

- New setup:
```
getmail/fetchmail -> procmail -> maildir-fake/boxes
maildelay (cron-job) -> maildir/boxes -> imapd/client
```

Example Rules
-------------
```
[DEFAULT]
default_buffer_mdir: ~/.maildir-fake
default_real_mdir: ~/.maildir

[Box:OpenBSD-tech]
buffer_mdir: %(default_buffer_mdir)s/OpenBSD
real_mdir: %(default_real_mdir)s/OpenBSD
rules: WorkCollect, Immediate

[Box:Gmail]
# yes it is clever enough to derive {buffer,real}_mdir
rules: Fixed, Immediate

[Rule:WorkCollect]
action: collect
from: 09:00
to: 17:00
for: 120

[Rule:Fixed]
action: fixed
at: 15:00, 20:00
```

Actions
-------
- immediate:
Immediately deliver mails. This is an implicit rule that is always
present.  It is mainly used in cascaded rules as the last rule. A
practical example could be a "Box" that specifies "rules:" as
"WorkCollect, Immediate". Therefore in the working hours "WorkCollect"
would match and the user does not get disturbed by high-traffic
mailing-lists. In the spare time "WorkCollect" does not match and
"Immediate" is executed, therefore mails are delivered instantly.

- collect:
If one mail in the buffer box is older than "for" minutes, all buffered mails
will be deliverd. This rule is perfect if you do not want to get
disturbed for the specified amount of minutes. It is like a mail digest
that is sent every "for" minutes. In between you do not get disturbed.

- fixed:
Deliver mails at the specified points in time. If the current time is
larger than the current "at" and the mail is oder than "at", it gets
delivered.

Todo
----
- Make it at least look like python and not like a drunken monkey wrote a
shell-script using python.
- More testing! It looks ok, what could possibly go wrong? For now it never
ever moves mails, it is always in "dry-run" mode.

Synopsis
--------
```
usage: maildelay.py [-h] [-c CONFFILE] [-f] [box [box ...]]

Delay mails and deliver them at specified points in time

positional arguments:
  box                   zero or more mailboxes matching names in
                        configuration. If none specified, all mailboxes are
                        processed.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFFILE, --config CONFFILE
                        path to configuration (~/.maildelay.cfg is the
                        default)
  -f, --flush           flush the given (or all) mailboxes (i.e., apply
                        Rule:Immediate)
```
