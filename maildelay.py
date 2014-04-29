#!/usr/bin/env python2

import ConfigParser
import argparse
import datetime
import os

I_KNOW_WHAT_I_DO = False

def collect(rule, src, dst):
    # check if current time is between from and to
    if config.has_option(rule, "from") and \
        config.has_option(rule, "to"):

        start_t = config.get(rule, "from")
        end_t = config.get(rule, "to")

        start_t = datetime.datetime.strptime(start_t, "%H:%M")
        end_t = datetime.datetime.strptime(end_t, "%H:%M")

        start_t = cur_t.replace(hour=start_t.hour, minute=start_t.minute)
        end_t = cur_t.replace(hour=end_t.hour, minute=end_t.minute)
        if not (start_t <= cur_t <= end_t):
            print "time not in range"
            return False
    else:
        print "rule has no from or no to"
        return False

    delta_t = datetime.timedelta(minutes=int(config.get(rule, "for")))

    move = False
    for mail in os.listdir(src):
        created_t = os.stat(os.path.join(src, mail)).st_mtime
        created_t = datetime.datetime.fromtimestamp(created_t)
        if created_t < (cur_t - delta_t):
            move = True
            break

    if move:
        for mail in os.listdir(src):
            srcf = os.path.join(src, mail)
            dstf = os.path.join(dst, mail)
            movefile(srcf, dstf)

    return True

def fixed(rule, src, dst):
    if config.has_option(rule, "at"):
        for opttime in config.get(rule, "at").strip().split(','):
            cfg_t = opttime.strip()
            check_t = datetime.datetime.strptime(cfg_t, "%H:%M")
            check_t = cur_t.replace(hour=check_t.hour, minute=check_t.minute)

            for mail in os.listdir(src):
                created_t = os.stat(os.path.join(src, mail)).st_mtime
                created_t = datetime.datetime.fromtimestamp(created_t)
                if cur_t >= check_t and created_t <= check_t:
                    srcf = os.path.join(src, mail)
                    dstf = os.path.join(dst, mail)
                    movefile(srcf, dstf)

    return True

def immediate(src, dst):
    for mail in os.listdir(src):
        srcf = os.path.join(src, mail)
        dstf = os.path.join(dst, mail)
        movefile(srcf, dstf)
    
    return True

def movefile(srcf, dstf):
    print "mv", srcf, dstf

    if I_KNOW_WHAT_I_DO:
        pass # os.renmae

def parsemaildir(box, option):
    if config.has_option(box, option):
        maildir = config.get(box, option)
    else:
        maildir = config.get("DEFAULT", "default_" + option)
        boxname = box[4:]
        maildir = os.path.join(maildir, boxname)

    if maildir.startswith('~'):
        maildir = os.path.expanduser(maildir)

    # TODO: stat/check if it is a dir
    # check for some nasty shit in path names?
    return os.path.join(maildir, "new")


# main
parser = argparse.ArgumentParser(description="Delay mails and deliver them at \
                                 specified points in time")
parser.add_argument('boxes', metavar="box", nargs='*',
                    help = "zero or more mailboxes matching names in \
                    configuration. If none specified, all mailboxes are \
                    processed.")
parser.add_argument("-c", "--config", dest = "conffile", default = \
                    "~/.maildelay.cfg", help = "path to configuration \
                    (~/.maildelay.cfg is the default)")
parser.add_argument("-f", "--flush", action='store_true', help = "flush the given (or\
                    all) mailboxes (i.e., apply Rule:Immediate)")
args = parser.parse_args()

config = ConfigParser.ConfigParser()
config.read([os.path.expanduser(args.conffile)])

# check if the config has a user defined "Immediate"-rule. If not, create one
if not config.has_section("Rule:Immediate"):
    config.add_section("Rule:Immediate")
    config.set("Rule:Immediate", "action", "immediate")

if args.boxes:
    boxes = []
    for box in args.boxes:
        boxes.append("Box:" + box)
else:
    boxes = config.sections()
    
cur_t = datetime.datetime.now()
for box in boxes:
    if box.startswith("Box:") and config.has_section(box):
        print "---", box, "---"

        srcmaildir = parsemaildir(box, "buffer_mdir")
        dstmaildir = parsemaildir(box, "real_mdir")
        if args.flush:
            immediate(srcmaildir, dstmaildir)
            continue

        if config.has_option(box, "rules"):
            for rule in config.get(box, "rules").strip().split(','):
                currule = rule.strip()
                currule = "Rule:" + currule
                print "evaluating", currule
                if config.has_section(currule):
                    print "valid rule:", currule

                    ret = False
                    # ok, rule valid, what is the action
                    if config.has_option(currule, "action"):
                        action = config.get(currule, "action")
                        if args.flush: action = "immediate"
                        ### collect ###
                        if action == "collect":
                            ret = collect(currule, srcmaildir, dstmaildir)
                        ### immediate ###
                        elif action == "immediate":
                            ret = immediate(srcmaildir, dstmaildir)
                        ### fixed ###
                        elif action == "fixed":
                            ret = fixed(currule, srcmaildir, dstmaildir)
                        else:
                            print "unknown action"
                        if ret: break
                    else:
                        print "rule has no action"
                else:
                    print "rule", currule, "does not exist"
        else:
            print "Box", box, "does not exist"
    
