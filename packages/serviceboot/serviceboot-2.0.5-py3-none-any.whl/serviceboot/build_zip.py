# -*- coding: utf-8 -*-
import os
import sys
import yaml
import shutil
import platform


def get_service_name():
    if not os.path.exists('requirements.txt'):
        print('错误： requirements.txt文件不存在！')
        return

    try:
        with open('./application.yml', 'rb') as f:
            yml = yaml.load(f, Loader=yaml.SafeLoader)
    except:
        print('错误： 微服务配置文件application.yml不存在！')
        return None

    try:
        name = yml['serviceboot']['cname']
    except:
        print('错误： 未指定微服务中文名！')
        print('请在application.yml文件中使用属性 serviceboot.cname 指定...')
        return None

    try:
        python_version = str(yml['serviceboot']['python_version'])
    except:
        print('错误： 未指定Python版本号！')
        print('请在application.yml文件中使用属性 serviceboot.python_version 指定...')
        return None

    if not python_version.startswith('3.'):
        print('错误： Python版本号必须是3且3.5以上！')
        print('请在application.yml文件中编辑修改...')
        return None

    if not sys.version.startswith(python_version):
        print('错误： 声明的Python版本号与当前运行环境（{}）不一致！'.format(sys.version[:sys.version.find(' ')]))
        print('请在application.yml文件中编辑修改...')
        return None

    return name


def build_zip():
    name = get_service_name()
    if name is None:
        return

    with open('./application.yml', 'rb') as f:
        yml = yaml.load(f, Loader=yaml.SafeLoader)

    try:
        build_web = yml['serviceboot']['has_web']
    except:
        build_web = False

    if platform.system() == 'Windows':
        os.system('rd /s /q out')
        os.system('mkdir out')
        os.system('mkdir out\\{}'.format(name))
        os.system('copy application.yml out\\{}\\'.format(name))
        os.system('copy requirements.txt out\\{}\\'.format(name))
        if os.path.exists('Dockerfile'):
            os.system('copy Dockerfile out\\{}\\'.format(name))
        if os.path.exists('README.md'):
            os.system('copy README.md out\\{}\\'.format(name))
        if os.path.exists('docs'):
            os.system('xcopy /y /q /s /e docs\\ out\\docs\\')
        os.system('mkdir out\\{}\\app'.format(name))
        os.system('xcopy /y /q /s /e app\\ out\\{}\\app\\'.format(name))
    else:
        os.system('rm -rf ./out')
        os.system('mkdir out')
        os.system('mkdir out/{}'.format(name))
        os.system('cp ./application.yml ./out/{}/'.format(name))
        os.system('cp ./requirements.txt ./out/{}/'.format(name))
        if os.path.exists('Dockerfile'):
            os.system('cp ./Dockerfile ./out/{}/'.format(name))
        if os.path.exists('README.md'):
            os.system('cp ./README.md ./out/{}/'.format(name))
        if os.path.exists('docs'):
            os.system('cp -r ./docs ./out/{}/'.format(name))
        os.system('cp -rf ./app ./out/{}/'.format(name))

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
                os.system('mkdir out\\{}\\webapp\\www'.format(name))
                os.system('xcopy /y /q /s /e webapp\\www\\ out\\{}\\webapp\\www\\'.format(name))
            else:
                os.system('mkdir out/{}/webapp'.format(name))
                os.system('cp -rf ./webapp/www ./out/{}/webapp/'.format(name))

    dst_path = './out/{}'.format(name)
    shutil.make_archive(dst_path, 'zip', dst_path)  # 将目标文件夹自动压缩成.zip文件
    shutil.rmtree('./out/{}/'.format(name))
    print('微服务打包完成！ 输出位置： ./out/{}.zip'.format(name))
