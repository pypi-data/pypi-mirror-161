import re
import pymysql
import pandas
import sqlalchemy


class MYSQL:
    """数据库链接"""

    def __init__(self, host, user, pwd, db):
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        engineStr = f"mysql+pymysql://{self.user}:{self.pwd}@{self.host}:3306/{self.db}"
        self.EE = sqlalchemy.create_engine(engineStr)

    def __GetConnect(self):
        if self.db:
            # noinspection PyBroadException
            try:
                self.conn = pymysql.connect(
                    host=self.host,
                    user=self.user,
                    password=self.pwd,
                    database=self.db,
                    use_unicode=True,
                    charset="utf8",
                )
            except Exception as e:
                exit("Don't a MySQL or MSSQL database.")
        else:
            exit("No database.")
        cur = self.conn.cursor()
        if not cur:
            exit("Error connect")
        else:
            return cur

    @staticmethod
    def tidySQL(sql):
        # sql = re.sub(r'\n\s*--sql\s*\n', ' ', sql) # 替换掉注释
        sql = re.sub(r"\s*\n\s*", " ", sql)  # 替换掉换行前后的空白
        return sql

    def ExecQuery(self, sql):
        """执行查询语句

        Args:
            sql(str) : 一条查询命令

        """
        cur = self.__GetConnect()
        cur.execute(sql)
        res = cur.fetchall()
        res_columns = ([i[0] for i in cur.description],)
        res = res_columns + res  ##res的第0个元素是标题。
        self.conn.close()
        return res

    def ExecNonQuery(self, sqlList):
        """执行修改语句

        Args:
            sql (list): 一组修改命令

        Returns:
            str: 成功1, 失败0.
        """
        cur = self.__GetConnect()
        ok = 0
        # noinspection PyBroadException
        try:
            [cur.execute(i) for i in sqlList]
            self.conn.commit()
            ok = 1
        except Exception as e:
            self.conn.rollback()
        self.conn.close()
        return ok

    @staticmethod
    def update_insert_sql(table, column, value):
        """
        table : 'table name'
        column: ['c1','c2','c3']
        value : ["(1,'2','a')","(2,'3','b')"]
        NOTES : `ON DUPLICATE KEY UPDATE`, UNIQUE INDEX is necessary.
        """
        sql_col = [f"`{i}`" for i in column]
        sql_val = ",\n".join(value)
        sql = f"""
            INSERT INTO {table}({','.join([_ for _ in sql_col])}) 
            VALUE  {sql_val}
            ON DUPLICATE KEY UPDATE {','.join([_ + '=VALUES(' + _ + ')' for _ in sql_col])}
        """
        sql = re.sub(r"\s*\n\s*", "\n", sql)  ##tidy
        return sql

    def dat2db(self, dat, tb):
        """将dataFrame格式数据导入数据库表tb，默认数据库链接。

        Args:
            dat (objct): dataframe
            tb (str):  tb name
            con (object) : 数据库连接

        Returns:
            str: 执行的sql
        """
        dat = dat.fillna("")
        dat = dat.dropna(axis="columns", how="all")
        dat = dat.applymap(lambda x: str(x))
        # 再出数据以前更新DAT列以匹配数据库列
        dbcol = set(self.ExecQuery(f"SELECT * FROM {tb} LIMIT 1")[0])
        dat = dat[dbcol.intersection(dat.columns)]
        # END
        sqlValue = []
        for _, e in dat.iterrows():
            ival = "('" + e[0] + "','" + "','".join(e[1:]) + "')"
            sqlValue.append(ival)
        sql = self.update_insert_sql(tb, list(dat.columns), sqlValue)
        self.ExecNonQuery([sql])
        return sql

    def datUpdateDB(self, dat, table, oncol, keycol, cond="1=1"):
        """数据dat更新到table。

        Args:
            dat (df): pandas 数据表
            table (str): 需要更新到的表名
            keycol (list): 表的关键字列表[index key list]
            ee (object) : 数据库连接方式2
            cond (str): 更新过程指定数据行的条件

        Returns:
            df: 更新到数据库的数据表
        """
        select_col = str(keycol)[1:-1].replace("'", "`")
        sql = f"""
            SELECT {select_col}
            FROM {table}
            WHERE {cond}
        """
        datDB = pandas.read_sql(sql, self.EE)
        datDBdropCol = [
            i for i in datDB.columns if (i not in oncol) and (i in dat.columns)
        ]  # * 依上传表格为准。
        datDB.drop(datDBdropCol, inplace=True, axis=1)
        dat = pandas.merge(dat, datDB, how="left", on=oncol)
        self.dat2db(dat, table)
        return dat
