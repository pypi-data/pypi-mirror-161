# -*- coding: utf-8 -*-
import os
import yaml
import platform


def build_docker():
    if not os.path.exists('Dockerfile'):
        print('错误： Dockerfile文件不存在！')
        return

    if not os.path.exists('requirements.txt'):
        print('错误： requirements.txt文件不存在！')
        return

    try:
        with open('./application.yml', 'rb') as f:
            yml = yaml.load(f, Loader=yaml.SafeLoader)
    except:
        print('错误： 模型配置文件application.yml不存在！')
        return

    try:
        image_name = str(yml['serviceboot']['ename'])
    except:
        print('错误： 未指定docker镜像名称！')
        print('请在application.yml文件中使用 serviceboot.ename 属性进行指定...')
        return

    try:
        image_tag = str(yml['serviceboot']['image_tag'])
    except:
        print('未指定docker镜像tag，使用：latest')
        image_tag = 'latest'

    try:
        build_web = yml['serviceboot']['has_web']
    except:
        build_web = False

    if platform.system() == 'Windows':
        os.system('rd /s /q temp')
        os.system('mkdir temp')
        os.system('xcopy /q application.yml temp')
        os.system('xcopy /q requirements.txt temp')
        os.system('xcopy /q Dockerfile temp')
        os.system('mkdir temp\\app')
        os.system('xcopy /y /q /s /e app temp\\app')
    else:
        os.system('rm -rf temp')
        os.system('mkdir temp')
        os.system('cp ./application.yml ./temp')
        os.system('cp ./requirements.txt ./temp')
        os.system('cp ./Dockerfile ./temp')
        os.system('cp -rf ./app ./temp/')

    if build_web:
        if os.path.exists('./webapp/src'):
            cwd = os.getcwd()
            os.chdir(os.path.join(cwd, 'webapp'))
            if not os.path.exists('./node_modules'):
                os.system('npm install')
            os.system('ng build --prod')
            os.chdir(cwd)
        if os.path.exists('./webapp/www'):
            if platform.system() == 'Windows':
                os.system('mkdir temp\\webapp\\www')
                os.system('xcopy /y /q /s /e webapp\\www temp\\webapp\\www')
            else:
                os.system('mkdir temp/webapp')
                os.system('cp -rf ./webapp/www ./temp/webapp/')

    os.system('docker image rm {}:{}'.format(image_name, image_tag))
    os.system('docker build -t {}:{} ./temp'.format(image_name, image_tag))
    if platform.system() == 'Windows':
        os.system('rd /s /q temp')
    else:
        os.system('rm -rf temp')

    print('微服务docker镜像 {}:{} 构建完成！ '.format(image_name, image_tag))
