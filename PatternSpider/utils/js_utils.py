#!/usr/bin/python3.8
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/13 17:36
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : js_utils.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved

#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
#
# @Time    : 2022/2/11 17:48
# @Author  : Feifan Liu
# @Email   : lff18731218157@163.com
# @File    : js_utils.py
# @Version : 1.0

# Copyright (C) 2022 北京盘拓数据科技有限公司 All Rights Reserved


class JsSentence:
    # 打开空白标签页的js语句 {} 填写打开的新页面要访问的地址
    open_new_label = 'window.open("{}");'
    # 获取鼠标下拉条，往下滑指定的长度 {} 填下拉的长度
    scroll_by = "window.scrollBy(0,{})"
    # 当前滚动条的高度
    scroll_height = "return document.body.scrollHeight;"
