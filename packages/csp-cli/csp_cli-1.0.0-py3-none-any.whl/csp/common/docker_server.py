#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/5/19 10:15
# @Author  : xgy
# @Site    : 
# @File    : docker_server.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import os
import time

import yaml
from csp.aip.common.http_client import HttpClient
from csp.common.config import Configure
from csp.common.utils import RunSys
from loguru import logger


class DockerServer:
    # 镜像容器端口，默认值
    def_port = "5000"
    def_param = ""

    def __init__(self, name, version, port, c_port=None, c_name=None, c_param=None, reload=True):
        self.name = name
        self.version = version
        self.port = port
        self.reload = reload
        self.container_name = c_name
        # 镜像容器端口灵活配置，默认5000
        self.container_port = self.def_port
        if c_port:
            self.container_port = c_port
        # 镜像启动参数
        self.container_param = self.def_param
        if c_param:
            self.container_param = c_param
        self.getter_container_name()
        self.interface_config = Configure().data
        self.http_client = HttpClient()
        self.image_url = None
        self.docker_client = None
        self.api_client = None
        self.check_env()

    def check_env(self):

        try:
            import docker
        except ImportError:
            logger.error("there is no docker try to install it, pip install docker")
            install_cmd = "pip install docker"
            install_cmd2 = "pip uninstall pywin32 -y"
            install_cmd3 = "pip install pywin32"

            RunSys(command=install_cmd).run_cli()
            RunSys(command=install_cmd2).run_cli()
            RunSys(command=install_cmd3).run_cli()

        import docker
        try:
            self.docker_client = docker.from_env()
        except docker.errors.DockerException:
            raise EnvironmentError("please start docker server first")

        self.api_client = docker.APIClient()

    def getter_container_name(self):
        if not self.container_name:
            container_name = self.name + "-v" + str(self.version)
            self.container_name = container_name

    def start(self):
        self.check_image()
        self.check_container()
        time.sleep(5)

    def stop(self):
        import docker
        container_stats = True
        # 需判断容器存在和容器运行
        is_container_running = False
        try:
            is_container_exists = self.docker_client.containers.get(self.container_name)
        except docker.errors.NotFound:
            logger.info("container not exists: {}".format(self.container_name))
            is_container_exists = False

        # container_l = docker_client.containers.get()
        container_l = self.docker_client.containers.list()
        for item in container_l:
            if item.name == self.container_name:
                is_container_running = True
                break

        if is_container_running and is_container_exists:
            stop_cmd = "docker stop " + self.container_name
            try:
                logger.info("the container {} is running, try to stop it".format(self.container_name))
                RunSys(stop_cmd).run_cli()
                time.sleep(10)
                container_l = self.docker_client.containers.list()
                for item in container_l:
                    if item.name == self.container_name:
                        logger.warning("the container {} stop failed".format(self.container_name))
                        break

                logger.info("the container {} stop success ".format(self.container_name))
                # logger.info("the container {} restart success".format(self.container_name))
            except:
                logger.error("stop container error: {}".format(stop_cmd))
                raise IOError("stop container error: " + stop_cmd)

    def check_container(self):
        import docker

        container_stats = True
        # 需判断容器存在和容器运行
        is_container_running = False
        try:
            is_container_exists = self.docker_client.containers.get(self.container_name)
        except docker.errors.NotFound:
            logger.info("container not exists: {}".format(self.container_name))
            is_container_exists = False

        if not is_container_exists:
            # run_cmd = "docker run -d --name " + self.container_name + " -p " + str(self.port) + ":" + "5000 " + self.image_url
            run_cmd = "docker run -d --name " + self.container_name + " " + self.container_param + " -p " + str(self.port) + ":" + str(self.container_port) + " " + self.image_url
            print(run_cmd)
            try:
                logger.info("run container from the {}".format(self.image_url))
                RunSys(run_cmd).run_cli()
                print("正等待容器服务启动。。。。。。")
                time.sleep(15)
                return container_stats
            except:
                # logger.error("start container error: {}".format(run_cmd))
                raise IOError("start container error: {}".format(run_cmd))

        # container_l = docker_client.containers.get()
        container_l = self.docker_client.containers.list()
        for item in container_l:
            if item.name == self.container_name:
                is_container_running = True
                break
        if is_container_running:
            res = self.api_client.inspect_container(self.container_name)
            container_port = res['HostConfig']['PortBindings'][self.container_port + '/tcp'][0]['HostPort']
            if str(self.port) != container_port:
                raise AttributeError("there is a container named " + self.container_name + " running, but the port is " + str(container_port) + ", please setting another container name by param 'c_name' or delete the old")
            logger.info("{} is running".format(self.container_name))
        if not is_container_running and is_container_exists:
            restart_cmd = "docker start " + self.container_name
            res = self.api_client.inspect_container(self.container_name)
            container_port = res['HostConfig']['PortBindings'][self.container_port + '/tcp'][0]['HostPort']
            if str(self.port) != container_port:
                raise AttributeError("there is a container named " + self.container_name + " exists, but the port is " + str(container_port) + ", please setting another container name by param 'c_name' or delete the old")
            try:
                logger.info("the container {} is exited but not running, try to restart it".format(self.container_name))
                RunSys(restart_cmd).run_cli()
                time.sleep(10)
                container_l = self.docker_client.containers.list()
                for item in container_l:
                    if item.name == self.container_name:
                        # is_container_running = True
                        logger.info("the container {} restart success".format(self.container_name))
                        break
                    else:
                        logger.warning("the container {} restart failed after 10 seconds".format(self.container_name))
                # logger.info("the container {} restart success".format(self.container_name))
            except:
                logger.error("restart container error: {}".format(restart_cmd))
                raise IOError("restart container error: " + restart_cmd)

    def check_image(self):
        import docker
        image_url = self.gen_image_info()
        self.image_url = image_url
        try:
            image = self.docker_client.images.get(image_url)
            logger.info("the image {} exited".format(image))
        except docker.errors.ImageNotFound:
            logger.warning("the image {} not found, will be download".format(self.image_url))
            # docker api，无日志输出
            # split_name = self.name.split(":")
            # repository = split_name[0] + ":" + split_name[1]
            # tag = split_name[2]
            # client.images.pull(repository=repository, tag=tag)
            # 命令行下载
            # pull_cmd = "docker pull " + self.name
            pull_cmd = "docker pull " + image_url
            cmd_statu = RunSys(pull_cmd).run_cli()
            if not cmd_statu:
                raise KeyError("pull docker image " + self.image_url + " error")

    def gen_image_info(self):
        """
        镜像版本获取
        1. 用户手动传入，暂不允许
        2. 使用reload=True 从后端获取最新版本
        3，从 docker_dict_path 中获取上一次记录
        4. 从本地查询获取
        5. 第三方服务版本与csp-cli版本绑定，不允许用户传入
        优先级顺序
        1. 使用reload=True 从后端获取最新版本
        2. 从本地查询获取
        3，从 docker_dict_path 中获取上一次记录
        """
        import docker
        parent_path = os.path.dirname(os.path.split(os.path.realpath(__file__))[0])
        docker_dict_path = os.path.join(parent_path, "common/config", "docker_dict.yaml")
        info = {"info": "the images dict"}
        if not os.path.exists(docker_dict_path):
            with open(docker_dict_path, "w", encoding="utf-8") as fw:
                yaml.dump(info, fw)

        url = self.interface_config["search"]["docker"]
        name = self.name
        params = {"name": name, "version": self.version}
        image_url_default = "192.168.54.151:28081/cspdevkit/aip" + ":" + self.name + "-v" + self.version

        if self.reload:
            # 像后端请求镜像地址
            logger.info("Query the image {} from the backend".format(image_url_default))
            res_dict = self.http_client.get(url, **params)
            if not res_dict["data"]:
                raise KeyError("Can not find image name: {} version {} from the backend".format(self.name, self.version))
            else:
                image_url = res_dict["data"]["url"]
                self.updata_docker_config(name, image_url, docker_dict_path)
        else:
            # 不向后端请求最新版地址，使用默认镜像配置，此时docker仓库地址为之前配置的
            # 先在本地查询
            logger.info("Query the image {} locally instead of requesting from the backend".format(image_url_default))
            try:
                self.docker_client.images.get(image_url_default)
                self.updata_docker_config(self.name, image_url_default, docker_dict_path)
                image_url = image_url_default
            except docker.errors.ImageNotFound:
                # 本地查询不存在该镜像，查询配置文件中地址
                logger.error("Can not query the image locally. The last downloaded image will be used")
                docker_dict = Configure(path=docker_dict_path).data
                image_url = docker_dict.get(self.name, 0)
                if not image_url:
                    # 配置文件中未找到该配置
                    logger.error("No usage record")
                    image_url = image_url_default
                    self.updata_docker_config(self.name, image_url_default, docker_dict_path)
                    # raise KeyError("No image found locally. Please use the parameter reload=true to download the image")

        return image_url

    def updata_docker_config(self, name, url, path):
        docker_dict = Configure(path=path).data
        docker_dict[name] = url
        with open(path, "w", encoding="utf-8") as fw2:
            yaml.dump(docker_dict, fw2)

    def net_is_used(self):
        """
        判断容器服务是否已启动完成
        1. time.sleep(10), 只有该方法有用
        2. socket
        3. api_client.inspect_container(self.container_name)
        4. self.docker_client.containers.list()
        5. 循环调用，使用res.status_code判断，当后端对请求处理是异步时，可能出错，如kg.create
        """
        res1 = self.api_client.inspect_container(self.container_name)
        time.sleep(10)
        res2 = self.api_client.inspect_container(self.container_name)

        print("debug")



if __name__ == '__main__':
    print("start")

    # server_name = "unst2st"
    # server_version = "0.3.2"
    # test_docker = DockerServer(name=server_name, version=server_version, port=9889, reload=False)
    # # test_docker = DockerServer(name=server_name, version=server_version, port=9889, reload=True)
    # # test_docker.check_image()
    # test_docker.image_url = "192.168.54.151:28081/cspdevkit/aip:unst2st-v0.3.2"
    # test_docker.check_container()


    server_name = "kg"
    server_version = "1.0"
    test_docker = DockerServer(name=server_name, version=server_version, port=30001, reload=False)
    # test_docker = DockerServer(name=server_name, version=server_version, port=9889, reload=True)
    # test_docker.check_image()
    test_docker.image_url = "192.168.54.151:28081/cspdevkit/aip:kg-v1.0"
    test_docker.check_container()



