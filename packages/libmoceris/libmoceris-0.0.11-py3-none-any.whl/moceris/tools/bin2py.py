"""
@author: bakabaka
@file:bin2py.py
@time:2022/2/4 16:06
@file_desc: 用于将静态文件转换为 py 文件，防止打包时丢失或改变目录
"""
import base64
import sys


def bin2py_unpack(res: str, dest: str):
    """
    释放一个 bin2py 打包的静态文件
    :param res: 源
    :param dest: 目标
    """
    try:
        with open(res, 'r') as fin:
            with open(dest, 'wb') as fout:
                base64.decode(fin, fout)
    except Exception as e:
        print(e)


def bin2py_pack(res: str, dest: str, inject: bool = False):
    """
    将一个静态文件转换为 py 文件
    :param res: 源
    :param dest: 目标文件
    :param inject: 是否内置提取函数
    """
    print(res,dest)
    try:
        with open(res, 'rb') as fin:
            opt = base64.b64encode(bytes(fin.read()))
            with open(dest, 'w',encoding='utf-8') as fout:
                fout.write('# packed by bin2py\n')
                fout.write('data={0}\n'.format(opt))
                if inject:
                    fout.write(
                        'import base64\n'
                        'def unpack(dest: str):\n'
                        '    """\n'
                        '    释放一个 bin2py 打包的静态文件\n'
                        '    :param dest: 目标\n'
                        '    """\n'
                        '    try:\n'
                        '        with open(dest, "wb") as fout:\n'
                        '            opt=base64.b64decode(data)\n'
                        '            fout.write(opt)\n'
                        '    except Exception as e:\n'
                        '        print(e)')
        print('finish.')
    except Exception as e:
        print(e)


def main():
    if len(sys.argv) == 1:
        print('too few arguments.')
    elif len(sys.argv) == 2:
        src = sys.argv[1]
        dest = src[:src.rfind('.')]+'_packed.py'
        bin2py_pack(src, dest, True)
    elif len(sys.argv) == 3:
        src = sys.argv[1]
        dest = sys.argv[2]
        bin2py_pack(src, dest, True)
    else:
        print('too much arguments.')
    input('press enter to exit...')


if __name__ == '__main__':
    main()
