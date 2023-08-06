# -*- coding: utf-8 -*-
import sys


def serviceboot_command():
    if len(sys.argv) < 2:
        print_usage()
        return

    cmd = sys.argv[1]

    if cmd == 'start':
        from . import serviceboot
        serviceboot.start()
        return

    if cmd == 'build_docker':
        from . import build_docker
        build_docker.build_docker()
        return

    if cmd == 'build_zip':
        from . import build_zip
        build_zip.build_zip()
        return

    if cmd == 'compile_python':
        from . import compile_python
        compile_python.compile_python()
        return

    if cmd == 'onboarding':
        from . import onboarding
        onboarding.onboarding()
        return

    print_usage()


def print_usage():
    print('serviceboot命令格式：')
    print('  serviceboot start             # 启动运行ServiceBoot微服务')
    print('  serviceboot build_docker      # 构建基于ServiceBoot的微服务docker镜像')
    print('  serviceboot build_zip         # 将基于ServiceBoot开发的微服务程序打包成zip文件，存放在out目录下')
    print('  serviceboot compile_python    # 将微服务程序中的Python代码编译成二进制代码，存放在build目录下')
    print('  serviceboot onboarding [URL]  # 将out目录下的AI模型压缩包发布至由[URL]所指定的CubeAI智立方算能服务平台')

