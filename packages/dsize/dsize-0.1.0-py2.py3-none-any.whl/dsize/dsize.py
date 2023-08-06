#============================================================
# Create Time:			2021-09-16 22:52:56
# Last modify:			2022-08-04 05:13:09
# Writer:				Wenhao	1795902848@qq.com
# File Name:			a.py
# File Type:			PY Source File
# Tool:					Mac -- vim & python
# Information:			
#============================================================
import os
import glob
import heapq
import argparse
import prettytable

import pdb

class SizeContainer():
    def __init__(this, prompt, size:int):
        this.prompt = prompt
        this.size = size

    def size_beautified(this, size):
        byte = size
        if byte < 1024:
            return '%d B'%(byte)

        k_byte = size >> 10
        if k_byte < 1024:
            return '%d KB'%(k_byte)

        m_byte = k_byte >> 10
        if m_byte < 1024:
            return '%d MB'%(m_byte)

        g_byte = m_byte >> 10
        return '%d GB'%(g_byte)

    def __str__(this):
        return '%s\t%s'%(this.size_beautified(this.size), this.prompt)

    def __add__(this, other):
        return SizeContainer(prompt='-- Total Size', size=this.size + other.size)

    def __lt__(this, other):
        return this.size < other.size

def build_args():
    parser = argparse.ArgumentParser('找到给定目录下，文件占据空间最大（不计算子目录所有文件的大小）的几个目录。\n')
    parser.add_argument('--dir', '-d', type=str, required=True, help='待递归遍历的目录。')
    parser.add_argument('--topk', '-k', type=int, required=False, help='只显示k个最大目录中所有文件的大小。', default=10)
    parser.add_argument('--exclude', '-e', type=str, required=False, help='要忽略的目录', default='', nargs='*')
    parser.add_argument('--wordy', '-w', required=False, help='是否要输出详细信息', default=False, action='store_true')
    parser.add_argument('--recur_depth', '-r', required=False, type=int, default=-1, help='递归的最大深度,不指定则无限制')
    parser.add_argument('--mode', '-m', required=False, type=str, default='folder', help='模式: 从[folder, file]中任选, 默认为folder.')
    args = parser.parse_args()
    return args

def walk(dirname, exclude_dirs=[], wordy=False, depth=-1):
    if dirname in exclude_dirs:
        return
    if not os.access(dirname, os.R_OK):
        if wordy:
            print('Have no access to: `%s`, skipped.'%(dirname))
        return
    try:
        fnames = os.listdir(dirname)
    except Exception as e:
        # pdb.set_trace()
        raise e

    fnames_isfile = []
    fnames_isdir = []
    for fname in fnames:
        path = os.path.join(dirname, fname)
        if os.path.isdir(path) and not os.path.islink(path):
            # print('path is dir:', path)
            fnames_isdir.append(fname)
            if path not in exclude_dirs:
                # print('path is dir and not in exclude_dirs', path)
                if depth == -1:
                    yield from walk(path, exclude_dirs, wordy, depth)
                elif depth >= 1:
                    yield from walk(path, exclude_dirs, wordy, depth-1)
        elif os.path.isfile(path):
            fnames_isfile.append(fname)
    yield dirname, fnames_isdir, fnames_isfile

def main():

    args = build_args()
    exclude_dirs = set(exclude.rstrip('/') for exclude in args.exclude if os.path.exists(exclude))
    if args.wordy:
        if not exclude_dirs:
            print('walking over everything')
        else:
            print('exclude dirs:', exclude_dirs)

    queue = []
    for dirname in glob.glob('%s*'%(args.dir)):
        if not os.path.isdir(dirname):
            continue
        for r, d, f in walk(dirname, exclude_dirs, wordy=args.wordy, depth=args.recur_depth):
            if args.mode == 'folder':
                size = sum([os.path.getsize(os.path.join(r, item)) for item in f])
                size = SizeContainer(prompt=r, size=size)
                heapq.heappush(queue, size)
                if len(queue) >= args.topk:
                    heapq.heappop(queue)

            elif args.mode == 'file':
                for item in f:
                    path = os.path.join(r, item)
                    size = os.path.getsize(path)
                    size = SizeContainer(prompt=path, size=size)
                    heapq.heappush(queue, size)
                    if len(queue) >= args.topk:
                        heapq.heappop(queue)


    table = prettytable.PrettyTable()
    table.field_names = ['序号', '大小', '目录']
    table.align['序号'] = 'r'
    table.align['大小'] = 'r'
    table.align['目录'] = 'l'
    size_sum = SizeContainer('', size=0)
    i = 1
    while queue:
        item = heapq.heappop(queue)
        table.add_row([i] + str(item).split('\t'))
        size_sum += item
        i += 1
    print(table)
    print(size_sum)

if __name__ == '__main__':
    main()
