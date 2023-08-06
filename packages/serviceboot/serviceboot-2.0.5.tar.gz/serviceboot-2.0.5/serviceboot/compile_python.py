# -*- coding: utf-8 -*-
import os
import sys
import yaml
import shutil
from distutils.core import setup
from Cython.Build import cythonize


class SoBuilder(object):
    def __init__(self, app_path):
        self.app_path = app_path
        self.base_path = os.path.abspath('.')
        self.build_path = 'build'
        self.build_tmp_path = 'build/tmp'
        if os.path.exists(self.build_path):
            shutil.rmtree(self.build_path)

        py_ver = ''.join(sys.version[0:3].split('.'))
        self.gcc_suffix = '.cpython-{}m-x86_64-linux-gnu.so'.format(py_ver)

    def copy_other_file(self, src_file_path):
        if src_file_path.endswith('__init__.py'):
            if os.path.exists(self.build_path):
                shutil.rmtree(self.build_path)
            raise Exception(print('程序中存在“__init__.py”文件，编译时会出现异常。请删除所有“__init__.py”文件后再编译！'))

        dst_file_path = '{}/{}/{}'.format(self.base_path, self.build_path, src_file_path[len(self.base_path) + 1:])
        dst_path = dst_file_path[:dst_file_path.rfind('/')]
        if not os.path.isdir(dst_path):
            os.makedirs(dst_path)
        shutil.copyfile(src_file_path, dst_file_path)

    def yeild_py(self, path, copy_others=True):
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            if os.path.isdir(file_path) and not file_name.startswith('.'):
                for f in self.yeild_py(file_path, copy_others):
                    yield f
            elif os.path.isfile(file_path):
                ext = os.path.splitext(file_name)[1]
                if ext not in ('.pyc', '.pyx'):
                    if ext == '.py' and not file_name.startswith('__'):
                        yield os.path.join(path, file_name)
                    elif copy_others:
                        self.copy_other_file(file_path)
            else:
                pass

    def delete_c_files(self, path):
        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            if os.path.isdir(file_path) and not file_name.startswith('.'):
                self.delete_c_files(file_path)
            elif os.path.isfile(file_path):
                ext = os.path.splitext(file_name)[1]
                if ext == '.c':
                    os.remove(file_path)
            else:
                pass

    def build_so(self):
        py_files = list(self.yeild_py(os.path.join(self.base_path, self.app_path)))

        try:
            for src_file_path in py_files:
                dst_file_path = '{}/{}/{}'.format(self.base_path, self.build_path,
                                                  src_file_path[len(self.base_path) + 1:])
                idx = dst_file_path.rfind('/')
                dst_path = dst_file_path[:idx]
                py_name = dst_file_path[idx + 1:].split('.')[0]
                setup(ext_modules=cythonize(src_file_path),
                      script_args=['build_ext', '-b', dst_path, '-t', self.build_tmp_path])
                src = dst_path + '/' + py_name + self.gcc_suffix
                dst = dst_path + '/' + py_name + '.so'
                os.rename(src, dst)
        except Exception as e:
            print(str(e))

        self.delete_c_files(os.path.join(self.base_path, self.app_path))
        if os.path.exists(self.build_tmp_path):
            shutil.rmtree(self.build_tmp_path)


def compile_python():
    if not os.path.exists('./app/app_core.py') and not os.path.exists('./app/app_main.py'):
        return

    with open('./application.yml', 'rb') as f:
        yml = yaml.load(f, Loader=yaml.SafeLoader)

    try:
        build_so = yml['serviceboot']['compile_python']
    except:
        build_so = False

    if build_so:
        so_builder = SoBuilder('app')
        try:
            so_builder.build_so()
        except:
            return

        app_profile = os.environ.get('APP_PROFILE', 'dev').lower()
        if app_profile == 'prod':
            os.system('rm -rf ./app')
            os.system('mv ./build/app .')
            os.system('rm -rf ./build')
