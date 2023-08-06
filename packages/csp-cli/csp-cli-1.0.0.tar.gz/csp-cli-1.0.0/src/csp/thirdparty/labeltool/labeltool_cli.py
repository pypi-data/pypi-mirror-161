#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/7/05 08:52
# @Author  : liny
# @Site    :
# @File    : labeltool_cli.py
# @Software: IDEA
# @python version: 3.7.4
"""
import click
from csp.command.cli import csptools
from csp.thirdparty import doccano

# from urllib.parse import urljoin

# 一级命令 CSP ocr
@csptools.group("labeltool")
def labeltool():
    """
    csp labeltool Command line
    """ 
## doccano启动
@labeltool.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-u", "--username", help="The administrator account in doccano project is admin by default", default=None)
@click.option("-e", "--email", help="The contact mailbox of the administrator in doccano project, which defaults to admin@example.com", default=None)
@click.option("-p", "--password", help="The administrator login password in doccano project is password by default", default=None)
def doccano_start(version, port, c_name, r, username, email, password):
    client = doccano(version=version, port=port, c_name=c_name, reload=r, d_username=username, d_email=email, d_password=password);
    client.start()

## doccano停止
@labeltool.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
def doccano_stop(version, port, c_name):
    client = doccano(version=version, port=port, c_name=c_name);
    client.stop()

@labeltool.command() 
@click.option("--url","-u", help="doccano url eg.http://192.168.18.25:8001", default="http://192.168.18.25:8001",type=str) 
@click.option("--username","-u", help="doccano username eg.admin", default="admin",type=str) 
@click.option("--password","-p", help="doccano password eg.password", default="password",type=str)
@click.option("--data_dir","-d", help="doccano file path eg.data/", default="output/uie",type=str)
@click.option("--file_name","-f", help="doccano filename eg.doccano_pred.json", default="doccano_pred.json",type=str)
@click.option("--project_type","-p", help="project type eg.SequenceLabeling", default="SequenceLabeling",type=str)
@click.option("--project_name","-n", help="project name eg.test", default="test",type=str) 
def doccano_import(url,username,password,data_dir,file_name,project_type,project_name):
    '''
    doccano 三元组标注数据导入
    '''
    doccano.imp(url, username, password, data_dir, file_name, project_type, project_name) 
    
@labeltool.command() 
@click.option("--url","-u", help="doccano url eg.192.168.18.25:8001", default="192.168.18.25:8001",type=str) 
@click.option("--username","-u", help="doccano username eg.admin", default="admin",type=str) 
@click.option("--password","-p", help="doccano password eg.password", default="password",type=str) 
@click.option("--project_name","-n", help="project name eg.test", default="test",type=str)
@click.option("--output_dir","-o", help="output dir eg.data/uie", default="output/uie",type=str)  
def doccano_export(url,username,password,project_name,output_dir):
    '''
    doccano 三元组标注数据导出
    '''
    doccano.exp(url, username, password, project_name, output_dir)