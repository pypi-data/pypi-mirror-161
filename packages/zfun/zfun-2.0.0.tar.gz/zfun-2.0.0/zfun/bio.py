
def humanChrName(cl=None):
    """生成染色体符号字典。

    Args:
        cl (可选列表): 指定列表。[1,2], [23,24,25]表示X、Y、M

    Returns:
        dict: 返回字典。id:str
    """
    if not cl:
        cl = list(range(1,23))
    chrD = {i: f"chr{i}" for i in cl}
    if 23 in cl:
        chrD[23] = "chrX"
    if 24 in cl:
        chrD[24] = "chrY"
    if 25 in cl:
        chrD[25] = "chrM"
    return chrD