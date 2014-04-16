#!/usr/bin/env python2

import os
from subprocess import Popen, PIPE

from munin import MuninPlugin


class UDLicensesPlugin(MuninPlugin):
    title = "Licenses"
    args = "--base 1000 -l 0"
    vlabel = "licenses"
    category = "ud"
    __total_licenses = 1000

    def __init__(self):
        super(UDLicensesPlugin, self).__init__()

        udbin = os.environ.get("udbin", "/usr/ud/bin")
        output = Popen("{0}/listuser".format(udbin), stdout=PIPE).communicate()[0]
        self.__total_licenses = int(output.split('\n')[3].split(' ')[5])

    @property
    def fields(self):
        return [
            ("fsp",
                dict(
                    label = "fsp",
                    info = 'Total number of used FSP licenses.',
                    min = "0",
                )
            ),
            ("pooled",
                dict(
                    label = "pooled",
                    info = 'Total number of pooled licenses.',
                    min = "0",
                )
            ),
            ("sql",
                dict(
                    label = "sql",
                    info = 'Total number of used SQL licenses.',
                    min = "0",
                )
            ),
            ("udt",
                dict(
                    label = "udt",
                    info = 'Total number of used UDT licenses.',
                    min = "0",
                )
            ),
            ("total",
                dict(
                    label = "total",
                    info = 'Total number of used licenses.',
                    min = "0",
                    warning = self.__total_licenses - 5,
                    critical = self.__total_licenses
                )
            )
        ]

    def execute(self):
        udbin = os.environ.get("udbin", "/usr/ud/bin")
        output = Popen("{0}/listuser".format(udbin), stdout=PIPE).communicate()[0]
        udt, sql, fsp, pooled, _, total = output.split('\n')[3].split('\t')[1:]

        return dict(
            fsp=fsp,
            pooled=pooled,
            sql=sql,
            total=total,
            udt=udt
        )

if __name__ == "__main__":
    UDLicensesPlugin().run()