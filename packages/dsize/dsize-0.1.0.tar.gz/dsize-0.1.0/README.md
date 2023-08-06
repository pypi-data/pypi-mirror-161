# 工具介绍
这是用来找目录中大文件的工具。
使用方法：
```bash
./dsize \
	-d ~/ \
	-e ~/Downloads ~/Desktop \
	-k 30
```

如上的参数意义是：
```text
-d：起始目录
-e：要忽略的目录，可以有数个
-k：最后要显示的占据空间最大的几个目录
```

eg:
```text
$ dsize -d ~/ -e ~/Library
exclude_dirs {'/Users/wh/Library'}
-Size--|-----Directions-------
9 MB	/Users/wh/Zotero/translators
12 MB	/Users/wh/Documents/git_clones/sentence-transformers/examples/applications/image-search
12 MB	/Users/wh/Zotero
15 MB	/Users/wh/Desktop/net_lecture
16 MB	/Users/wh/Documents/git_clones/sentence-transformers/.git/objects/pack
86 MB	/Users/wh/Documents/LearnRecords/PPT
110 MB	/Users/wh/Documents/MarginNote 3 User Guide videos
147 MB	/Users/wh/usr/bin
176 MB	/Users/wh/Documents/group_meeting/2021-10-10
```
