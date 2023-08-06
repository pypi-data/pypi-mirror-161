#-* -coding: UTF-8 -* -


import sys, os, shutil, time
from distutils.core import setup
from Cython.Build import cythonize

starttime = time.time()
# currdir = os.path.abspath('.')
currdir = r'D://work//study//PYEX//model_lib//deploy//win64//Automan//'
os.chdir(currdir)
# parentpath = sys.argv[1] if len(sys.argv)>1 else ""
parentpath = ""
# setupfile= os.path.join(os.path.abspath('.'), __file__)
setupfile=currdir + 'batch_setup.py'
build_dir = "build"
build_tmp_dir = build_dir + "/temp"

def getpy(basepath=os.path.abspath('.'), parentpath='', name='', excepts=(), copyOther=False,delC=False):
    """
    获取py文件的路径
    :param basepath: 根路径
    :param parentpath: 父路径
    :param name: 文件/夹
    :param excepts: 排除文件
    :param copy: 是否copy其他文件
    :return: py文件的迭代器
    """
    fullpath = os.path.join(basepath, parentpath, name)
    for fname in os.listdir(fullpath):
        ffile = os.path.join(fullpath, fname)
        print ("ffile=",ffile)
        #print basepath, parentpath, name,file
        if os.path.isdir(ffile) and fname != build_dir and not fname.startswith('.'):
            for f in getpy(basepath, os.path.join(parentpath, name), fname, excepts, copyOther, delC):
                yield f
        elif os.path.isfile(ffile):
            ext = os.path.splitext(fname)[1]
            if ext == ".c":
                # print (os.stat(ffile).st_mtime > starttime)
                # if delC and os.stat(ffile).st_mtime > starttime:
                if delC :
                    os.remove(ffile)
            elif ffile not in excepts and os.path.splitext(fname)[1] not in('.pyc', '.pyx'):
                if os.path.splitext(fname)[1] in ('.py', '.pyx') and not fname.startswith('__'):
                    yield os.path.join(parentpath, name, fname)
                elif copyOther:
                        dstdir = os.path.join(basepath, build_dir, parentpath, name)
                        if not os.path.isdir(dstdir): os.makedirs(dstdir)
                        shutil.copyfile(ffile, os.path.join(dstdir, fname))
        else:
            pass

#获取py列表
module_list = list(getpy(basepath=currdir,parentpath=parentpath, excepts=(setupfile)))
try:
    setup(ext_modules = cythonize(module_list),script_args=["build_ext", "-b", build_dir, "-t", build_tmp_dir])
except Exception as ex:
    print ("error! ", ex)
else:
    module_list = list(getpy(basepath=currdir, parentpath=parentpath, excepts=(setupfile), copyOther=True))

module_list = list(getpy(basepath=currdir, parentpath=parentpath, excepts=(setupfile), delC=True))
if os.path.exists(build_tmp_dir): shutil.rmtree(build_tmp_dir)

print ("complate! time:", time.time()-starttime, 's')


def rename(file):
    ''' file: 文件路径'''
    os.chdir(file)
    items = os.listdir(file)
    print(os.getcwd())
    for name in items :
        print(name)
        # 遍历所有文件
        if not os.path.isdir(name):
            if  len(name.split('.')) == 3 and os.path.splitext(name)[1]  in ('.pyd', '.so') :
                new_name = name.replace('.' + name.split('.')[1],'')
                # os.renames(name,new_name)
                shutil.move(name,new_name)
        else:
            print("dir:",file + '//' + name)
            rename(file + '//' + name)
            print ("bef",os.getcwd())
            os.chdir('../')
            print ("aft",os.getcwd())
    print('-----------------------分界线------------------------')
    items = os.listdir(file)
    for name in items:
        print(name)
rename(currdir + build_dir)
