#!/usr/bin/env python2

import os
from os import linesep
from subprocess import Popen, PIPE

from munin import MuninPlugin


class UDReplicationLagPlugin(MuninPlugin):
    title = "LSN lag"
    args = "--base 1000 -l 0"
    vlabel = "LSNs behind"
    category = "ud"

    @property
    def fields(self):
        return [
            ("publisher", dict(
                label="publisher",
                info='LSN lag on the publisher.',
                colour="22ff22",  # Green
                min="0",
            )),
            ("subscriber", dict(
                label="subscriber",
                info='LSN lag on the subscriber.',
                colour="ff0000",  # Red
                min="0",
            )),
        ]

    def execute(self):
        local_done_lsn = remote_done_lsn = next_avail_lsn = 0
        udbin = os.environ.get("udbin", "/usr/ud/bin")
        groups = int(os.environ.get("groups", 8))

        # Answers to reptool prompts.  This will display data for the number of groups specified in the config
        # file, defaulting to 8 groups.
        answers = linesep.join(["2{1}{0}{1}3{1}4{1}".format(g, linesep) for g in xrange(groups)]) + (linesep * 2)

        # Pipe in our answers and pipe out the output.
        output = Popen("{0}/reptool".format(udbin), stdin=PIPE, stdout=PIPE).communicate(answers)[0]

        for line in output.split(linesep):
            if "RB pointers of Group" in line:
                groups += 1
            elif "localDoneLSN:" in line:
                local_done_lsn += int(line.split(':')[1].strip())
            elif "remoteDoneLSN =" in line:
                remote_done_lsn += int(line.split('=')[1].strip())
            elif "nextAvailLSN:" in line:
                next_avail_lsn += int(line.split(':')[1].strip())

        return dict(
            publisher=next_avail_lsn - groups - local_done_lsn,
            subscriber=local_done_lsn - remote_done_lsn
        )

if __name__ == "__main__":
    UDReplicationLagPlugin().run()