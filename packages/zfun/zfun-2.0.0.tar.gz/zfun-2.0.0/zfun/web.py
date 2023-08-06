import dash_mantine_components as dmc
import requests
import base64
import os
from io import BytesIO, StringIO
import pandas


import dash_tabulator.DashTabulator as Table


def webPost(url, p=None):
    """
    请求url(post), 配合fastapi接口使用。p为列表。

    Args:
        url (url): url
        p (list): 必须是tuple或者list

    Returns:
        requtest object: json
    """
    r = requests.post(url, json=p, headers={"content-type": "application/json"})
    data = r.json()
    return data


def ctxIndex(ctx):
    """dash plotly 小功能。获取当前出发的组件的索引。

    Args:
        ctx (object) : dash 对象

    Returns:
        触发组件的位置
    """
    if ctx.triggered_id:
        return [i["id"] for i in ctx.inputs_list].index(ctx.triggered_id)


def webTab(df, export=False, other_opt={}):
    """返回一个前端表格。简单版本。

    Args:
        df (pandas dataframe): 要显示的数据表
        export (bool, optional): 是否显示导出按钮. Defaults to False.
        other_opt (dict, optional): 其他表格控制选项. Defaults to {}.

    Returns:
        dash 组件: 返回dash组件
    """
    opt = {}
    opt["theme"] = "tabulator_simple"
    opt["col"] = {i: {"title": i, "field": i} for i in df.columns}
    opt["data"] = df.to_dict("records")
    opt["cellDblClick"] = True
    opt["options"] = {
        "selectable": False,
        "layout": "fitDataStretch",
        "pagination": "local",
        "paginationSize": 10,
        "paginationSizeSelector": [10, 20, 50, 100],
        "movableColumns": True,
    }
    if export:
        opt["downloadButtonType"] = {
            "css": "btn btn-primary",
            "text": "导出",
            "type": "xlsx",
        }
    # 其他参数的更新
    new_opt = dict(opt, **other_opt)
    for k in new_opt.keys():
        if isinstance(new_opt[k], dict) and k in opt and isinstance(opt[k], dict):
            new_opt[k] = dict(new_opt[k], **opt[k])

    # 处理成默认参数
    new_opt["columns"] = list(new_opt["col"].values())
    del new_opt["col"]

    return Table(**new_opt)


def webDoc(notes, showList=True, showlab="展开", hidelab="收起", maxH=0):
    """生成折叠式的注释。

    Args:
        notes (字典): {"使用说明A：":['1','2',...], "使用说明B：":[]}

    Returns:
        dmc折叠组件。
    """

    c = []
    for i, v in notes.items():
        c.append(i)
        if showList:
            c.append(
                dmc.List(
                    [dmc.ListItem(j) for j in v],
                    withPadding="8px",
                    type="ordered",
                )
            )
        else:
            c.extend(v)

    notes = dmc.Spoiler(
        showLabel=showlab,
        hideLabel=hidelab,
        maxHeight=maxH,
        children=c,
    )
    return notes


def dccfileSave(fc, fn=None, path=None, format="xls", sheet_name=None):
    """保存dccfile控件的文件

    Args:
        fc (bin): dcc file控件的文件内容
        fn (str): dcc file控件的文件名称
        path (str, optional): path不为空输出到文件，否则返回df. Defaults to None.

    Returns:
        多情况: path+fn 或者 pandas.DataFrame
    """
    f_content = fc.encode("utf8").split(b";base64,")[1]  # 读取文件内容。
    f_content = base64.b64decode(f_content)
    if path:
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + fn, "wb") as f:
            f.write(f_content)
        return path + fn
    if format == "xls":
        df = pandas.read_excel(BytesIO(f_content), sheet_name=sheet_name)
    elif format == "csv":
        df = pandas.read_csv(StringIO(f_content.decode("utf-8")))
    elif format == "tsv":
        df = pandas.read_csv(StringIO(f_content.decode("utf-8")), sep="\t")
    return df


def webTabEdit():
    # todo
    "生产一个可编辑的表格，编辑后可以返回dataFrame"
    ...
