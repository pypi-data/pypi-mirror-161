#!/usr/bin/env python
# encoding: utf-8  
from csp.command.cli import csptools 
# 一级命令 csp pipeline
@csptools.group("pipeline")
def pipeline():
    """
    csp pipeline Command line \n the tools for pipeline
    """

if __name__ == '__main__':
    print("start")
