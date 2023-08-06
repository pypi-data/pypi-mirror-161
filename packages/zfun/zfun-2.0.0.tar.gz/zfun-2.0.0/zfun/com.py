from time import localtime, strftime
import os
import winrm
import PyPDF2


def nowf(former="t"):
    """格式化当前时间

    Args:
        former (str, optional): Defaults to "t".
            "s" : 20220730121212
            "t" : 2022-07-30 12:12:12
            "d" : 2022-07-30

    Returns:
        str: 返回时间字符串
    """
    person = {"s": "%Y%m%d%H%M%S", "t": "%Y-%m-%d %H:%M:%S", "d": "%Y-%m-%d"}
    # noinspection PyBroadException
    try:
        former = person.get(former, former)
        return strftime(former, localtime())
    except Exception as e:
        print("不合法的时间格式")


def mkdirf(pathf):
    """如果不存在则创建

    Args:
        pathf (str): 文件夹路径

    Returns:
        str: 返回创建的文件夹的绝对路径
    """
    if not os.path.exists(pathf):
        os.mkdir(pathf)
    return os.path.abspath(pathf)


def mkscript(fpath, s):
    """创建一个可执行的文件。

    Args:
        fpath (str): 文件绝对路径
        s (str): 可执行的命令
    """
    fpath = os.path.abspath(fpath)
    with open(fpath, "w") as f:
        f.write(s + "\n")
    os.system("chmod +x " + fpath)


def winCMD(cmd, ip, user, password):
    """远程执行Windows任务。

    Args:
        cmd (str): 任务命令
        ip (str): 远程电脑ip
        user (str): 可登录用户
        password (str): 用户密码

    Returns:
        _type_: _description_
    """
    win = winrm.Session(f"http://{ip}:5985/wsman", auth=(user, password))
    r = win.run_cmd(cmd)
    out = r.std_out.decode("gbk")
    err = r.std_err.decode("gbk")
    return out, err


def pdfMerger(pdf_list, pdf_out):
    """合并多个pdf

    Args:
        pdf_list (list): 需要合并的PDF路径列表
        pdf_out (str): 合并后的输出路径
    """
    merger = PyPDF2.PdfFileMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(pdf_out)
    merger.close()
    return pdf_out


def pdfPaste(file_marker, file_in, pnum=0, file_out=None):
    """覆盖2个pdf文件。

    Args:
        file_marker (str): 水印文件
        file_main (str): 主文件
        file_out (str): 输出文件
    """
    pdf_watermark = PyPDF2.PdfFileReader(open(file_marker, "rb"))
    pdf_input = PyPDF2.PdfFileReader(file_in)
    pdf_output = PyPDF2.PdfFileWriter()
    pageCount = pdf_input.getNumPages()
    for i in range(pageCount):
        if i - pnum in [0, pageCount]:  # test 负号表示倒数
            page = pdf_input.getPage(i)
            page.mergePage(pdf_watermark.getPage(0))
            page.compressContentStreams()
            pdf_output.addPage(page)
        else:
            pdf_output.addPage(pdf_input.getPage(i))
    if not file_out:
        file_out = file_in
    pdf_output.write(open(file_out, "wb"))


def text2Range(t, k=4):
    """生产序列文件， 主要用于数据库查询。

    Args:
        t (str): 多行字符串
            1. !ada-3 : 叹号开始表示一个字符串，忽略 -
            2. adab : 没有 - 表示一个字符串
            3. A001-A012 : - 表示范围
        k (int, optional): 末尾多少位是序列. Defaults to 4.

    Returns:
        list: 返回所有的数据
    """
    if not t:
        return "格式不正确"
    t = t.strip()
    sampleSet = []
    for i in t.split("\n"):
        iline = i.strip().replace("\r", "")
        if iline[0] == "!" or iline.count("-") == 0:
            sampleSet.append(iline.replace("!", ""))
            continue
        if iline.count("-") == 1:
            start, end = iline.split("-")
            ifix, ifix2 = start[:k], end[:k]
            if ifix != ifix2:
                return "前缀不一致"
            istart = int(start[-k:])
            iend = int(end[-k:])
            for j in range(istart, iend + 1):
                suffix = str(j + 10**k)[1:]
                sampleSet.append(ifix + suffix)
    return sampleSet


def remove_upprintable_chars(s):
    """移除字符串中的不可见字符

    Args:
        s : 字符串
    """

    if s:
        return "".join(x for x in str(s) if x.isprintable())


if __name__ == "__main__":
    ...
