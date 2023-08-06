#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/7/05 08:52
# @Author  : liny
# @Site    :
# @File    : doccano.py
# @Software: IDEA
# @python version: 3.7.4
"""
from csp.common.docker_server import DockerServer
from csp.thirdparty.labeltool.doccano_api_client import DoccanoClient 
import os,zipfile

def get_project_id(doccano_client,project_name):
    project_list = doccano_client.get_project_list() 
    for project in project_list['results']:
        if project_name == project['name']:
            return project['id']
    return -1

def doccano_client_init(url,username,password):   
    # path = 'luotuofeile'
    # URL_PATH = urljoin(url,path) 
    doccano_client = DoccanoClient(
        url,
        username,
        password
    ) 
    return doccano_client

class doccano:
    # 镜像版本号，默认值
    def_version = "1.0"
    # 镜像容器端口，默认值
    def_port = "8000"
    # 镜像容器内端口，默认值
    def_c_port = "8000"
    # 镜像名称，默认值
    def_name = "doccano"
    # 镜像启动参数，默认值
    def_username = "admin"
    def_email = "admin@example.com"
    def_password = "admin"

    def __init__(self, version=None, port=None, name=None, c_port=None, c_name=None, reload=True, d_username=None, d_email=None, d_password=None):
        self.version = self.def_version
        self.port = self.def_port
        self.name = self.def_name
        self.c_port = self.def_c_port
        self.d_username = self.def_username
        self.d_email = self.def_email
        self.d_password = self.def_password

        if version:
            self.version = version
        if port:
            self.port = port
        if name:
            self.name = name
        if c_port:
            self.c_port = c_port
        if d_username:
            self.d_username = d_username
        if d_email:
            self.d_email = d_email
        if d_password:
            self.d_password = d_password

        self.c_param = '-e "ADMIN_USERNAME=' + self.d_username + '" -e "ADMIN_EMAIL=' + self.d_email + '" -e "ADMIN_PASSWORD=' + self.d_password + '"'
        self.server = DockerServer(name=self.name, version=self.version, port=self.port, c_name=c_name, c_param=self.c_param, c_port=self.c_port, reload=reload)
        #self.server.start()


    def start(self):
        self.server.start()
        print("==============doccano==============")
        print("http://127.0.0.1:" + self.port)
        print("username:" + self.d_username)
        print("password:" + self.d_password)
        print("==============end==================")

    def stop(self):
        self.server.stop(); 

    @staticmethod
    def imp(url='http://127.0.0.1:8000',
            username='admin',
            password='password',
            data_dir='output/uie',
            file_name='doccano_pred.json',
            project_type='SequenceLabeling',
            project_name='uiespo' 
            ):
        '''
        doccano 三元组标注数据导入
        Args:
            url : doccano url eg.http://127.0.0.1:8000
            username : doccano username eg.admin
            password : doccano password eg.password
            data_dir : doccano file path eg.output/uie
            file_name : doccano filename eg.doccano_pred.json
            project_type : project type eg.SequenceLabeling
            project_name : project name eg.uiespo
        Returns:
        ''' 
        doccano_client = doccano_client_init(url, username, password)
        project_id = get_project_id(doccano_client,project_name)
        if project_id >= 0 :
            doccano_client.delete_project(project_id) 
        
        doccano_client.create_project(project_name, project_name, project_type)
        
        project_id = get_project_id(doccano_client,project_name)
        rs = doccano_client.post_doc_upload(project_id,file_name, data_dir)
        print(rs)  
    
    @staticmethod   
    def exp(url='http://127.0.0.1:8000',
            username='admin',
            password='password',
            project_name='uiespo',
            output_dir='output/uie'
            ):
        '''
        doccano 三元组标注数据导出
        Args: 
            url : doccano url eg.http://127.0.0.1:8000
            username : doccano username eg.admin
            password : doccano password eg.password
            project_name : project name eg.uiespo
            output_dir : output dir eg.data/uie
        Returns:
        '''  
        doccano_client = doccano_client_init(url, username, password)
        project_id = get_project_id(doccano_client,project_name)
        if project_id >=0 : 
            result = doccano_client.get_doc_download(project_id)  
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir,f'{project_id}.zip') 
            with open(output_file, 'wb') as f:
                for chunk in result.iter_content(chunk_size=8192): 
                    f.write(chunk) 
            
            zfile = zipfile.ZipFile(output_file,'r') 
            for filename in zfile.namelist():  
                data = zfile.read(filename) 
                file = open(os.path.join(output_dir,filename), 'w+b') 
                file.write(data) 
                file.close() 
            print('download file:',output_file)
            srcFile = os.path.join(output_dir,'admin.jsonl')
            dstFile = os.path.join(output_dir,'doccano_ext.json')
            if os.path.exists(dstFile):
                os.remove(dstFile)
            os.rename(srcFile,dstFile)
            print('doccano pred file:',dstFile)
    
if __name__ == '__main__':
    print("start doccano")
    doccano = doccano()
    #doccano.start()
    doccano.stop()