import pymysql
import pandas as pd

# ====================================
# 用于连接Mysql数据库
# 更新时间: 2021-04-07

# 函数目录:
# 1.PRINT_LOG -- 是否打印全局修改
# 2.SQL_EXECUTE -- 执行一条sql语句
# 3.SQL2df -- 读取数据库形成DataFrame
# 4.INSERT_RAW_DATA -- 将DataFrame写入数据库
# 5.UpdateSQL -- 将DataFrame写入并更新数据库(旧)
# 6.UpdateSQL2 -- 将DataFrame写入并更新数据库(新)
# 7.Add_Col -- 数据表添加新列
# 8.Delete_Row -- 数据表删除行
# ====================================

# =========== 服务器信息 ==============
SERVER_ADDRESS = 'localhost'
SERVER_USER = 'root'
SERVER_PASSWORD = '123'

PRINT = True
# ====================================


def PRINT_LOG(x):
    """设置是否打印所执行的SQL语句, 默认为True.

    parameters:
    x -- True/False
    """

    global PRINT
    PRINT = x


def SetServerInfo(host, user, password):
    """设置服务器信息.

    parameters:
    host -- 服务器ip
    user -- 数据库账户名
    password -- 数据库账户密码
    """

    global SERVER_ADDRESS, SERVER_USER, SERVER_PASSWORD
    SERVER_ADDRESS = host
    SERVER_USER = user
    SERVER_PASSWORD = password


def SQL_EXECUTE(LINE):
    """执行一条sql语句

    参数:
    LINE -- str, sql语句
    """

    db = pymysql.connect(host=SERVER_ADDRESS,
                         user=SERVER_USER,
                         password=SERVER_PASSWORD)
    cursor = db.cursor()
    cursor.execute(LINE)
    db.commit()
    if PRINT:
        print("EXECUTE SQL:", LINE)
    cursor.close()
    db.close()


def describe_table(database, table):
    db = pymysql.connect(host=SERVER_ADDRESS,
                         user=SERVER_USER,
                         password=SERVER_PASSWORD)
    cursor = db.cursor()
    SQL = 'describe `%s`.`%s`'%(database, table)
    cursor.execute(SQL)
    res = cursor.fetchall()
    col = list(pd.DataFrame(cursor.description)[0])
    df = pd.DataFrame(res, columns=col)
    db.commit()
    if PRINT:
        print("EXECUTE SQL:", SQL)
    cursor.close()
    db.close()

    return df


def SQL2df(database, table, params='*', **kwargs):
    """读取SQL数据生成DataFrame格式

    参数:
    database -- Schema名称
    table -- 数据表名称
    params -- list,变量名称
    kwargs:
        code -- str or list, 证券代码，含（.OF）
        date -- "YYYY-MM-DD", 净值时间点
        start_date -- 起始时间
        end_date -- 终止时间
        cate -- dict, 其他筛选条件
        limit -- 最大行数
        include -- “包含”筛选
    """

    if params != '*':
        params_str = ''
        for i in range(len(params)):
            params_str += '`' + params[i] + '`'
            if i != len(params) - 1:
                params_str += ','
    else:
        params_str = params

    db = pymysql.connect(host=SERVER_ADDRESS,
                         user=SERVER_USER,
                         password=SERVER_PASSWORD,
                         database=database)
    cursor = db.cursor()
    df = pd.DataFrame()
    try:
        SQL = "SELECT %s FROM `%s`.`%s`" % (params_str, database, table)
        WHERE = False
        if 'code' in kwargs:
            if 'code_label' in kwargs:
                LABEL = kwargs['code_label']
            else:
                LABEL = '基金代码'
            WHERE = True
            if type(kwargs['code']) != list:
                SQL += " where `%s`='%s'" % (LABEL, kwargs['code'])
            else:
                SQL += " where %s in (" % LABEL
                CODEs = kwargs['code']
                for i in range(len(CODEs)):
                    SQL += "'%s'" % CODEs[i]
                    if i != len(CODEs) - 1:
                        SQL += ","
                SQL += ')'
        if 'date' in kwargs:
            if WHERE is True:
                SQL += " AND"
            else:
                SQL += " where"
                WHERE = True
            SQL += " `日期`='%s'" % kwargs['date']

        if ('start_date' in kwargs) and (kwargs['start_date'] is not None):
            if WHERE is True:
                SQL += " AND"
            else:
                SQL += " where"
                WHERE = True
            SQL += " `日期`>='%s'" % kwargs['start_date']

        if ('end_date' in kwargs) and (kwargs['end_date'] is not None):
            if WHERE is True:
                SQL += " AND"
            else:
                SQL += " where"
                WHERE = True
            SQL += " `日期`<='%s'" % kwargs['end_date']
        if 'cate' in kwargs:
            cate = kwargs['cate']
            if WHERE is True:
                SQL += " AND"
            else:
                SQL += " where"
                WHERE = True
            n = 0
            for keys in cate:
                n += 1
                if n > 1:
                    SQL += " AND"
                SQL += " `%s`='%s'" % (keys,cate[keys])
        if 'include' in kwargs:
            include = kwargs['include']

            if WHERE is True:
                SQL += " AND"
            else:
                SQL += " where"
                WHERE = True
            n = 0
            for keys in include:
                n += 1
                if n > 1:
                    SQL += " AND"
                SQL += " locate('%s',`%s`)" % (include[keys],keys)
        if 'limit' in kwargs:
            SQL += ' limit %s'%kwargs['limit']
        if PRINT:
            print("EXECUTE SQL:", SQL)
        cursor.execute(SQL)
        res = cursor.fetchall()
        col = list(pd.DataFrame(cursor.description)[0])
        df = pd.DataFrame(res, columns=col)
    except(Exception):
        db.rollback()
        print("SQL2df Error!")

    cursor.close()
    db.close()

    return df


def INSERT_RAW_DATA(df, database, table):
    """向数据库插入数据

    参数:
    df -- DataFrame数据
    database -- 数据库名
    table -- 数据表名
    """

    db = pymysql.connect(host=SERVER_ADDRESS,
                         user=SERVER_USER,
                         password=SERVER_PASSWORD,
                         database=database)
    cursor = db.cursor()
    SQL = "INSERT INTO `%s`.`%s` (" % (database, table)
    for i in range(len(df.columns)):
        SQL += "`%s`" % df.columns[i]
        if i != len(df.columns) - 1:
            SQL += ","
    SQL += ") VALUES ("
    for i in range(len(df.columns)):
        SQL += "%s"
        if i != len(df.columns) - 1:
            SQL += ","
    SQL += ");"
    v = []
    A = tuple(df.itertuples(index=False, name=None))
    for i in range(len(A)):
        v.append([])
        for j in range(len(A[i])):
            item = A[i][j]
            if item == 'None':
                item = None
            elif item == 'nan':
                item = None
            elif item == '':
                item = None
            elif item != item:
                item = None
            elif item == 'NaT':
                item = None
            v[i].append(item)
        v[i] = tuple(v[i])
    v = tuple(v)
    if PRINT:
        print("EXECUTE SQL:", SQL)
    cursor.executemany(SQL, v)
    db.commit()
    cursor.close()
    db.close()


def UpdateSQL(df, database, table, bys, INSERT_NEW=True):
    """写入并更新数据库

    参数:
    df -- DataFrame格式数据
    host -- 服务器地址
    database -- 数据库名称
    table -- 数据表名称
    bys -- 数据库列名, 依据此列更新数据库
    """

    df0 = SQL2df(database, table, bys).astype(str).set_index(bys)
    df = df.astype(str).set_index(bys)
    old_index, new_index = [], []
    for i in df.index:
        if i in df0.index:
            old_index.append(i)
        else:
            new_index.append(i)
    df_old = df.loc[old_index, :].reset_index()
    df_new = df.loc[new_index, :].reset_index()

    if PRINT:
        print('===df_old========================')
        print(df_old)
        print('===df_new========================')
        print(df_new)

    df_old = pd.DataFrame.join(df_old.drop(bys, axis=1), df_old[bys])
    db = pymysql.connect(host=SERVER_ADDRESS,
                         user=SERVER_USER,
                         password=SERVER_PASSWORD,
                         database=database)
    cursor = db.cursor()

    col = df_old.drop(bys, axis=1).columns
    SQL = "UPDATE `%s`.`%s` SET " % (database, table)
    for i in range(len(col)):
        SQL += "`%s`=%%s" % col[i]
        if i != len(col) - 1:
            SQL += ','
    SQL += " WHERE"
    for j in range(len(bys)):
        SQL += " (`%s` = %%s)" % bys[j]
        if j != len(bys) - 1:
            SQL += " AND"
    SQL += ';'
    v = []
    A = tuple(df_old.itertuples(index=False, name=None))
    for i in range(len(A)):
        v.append([])
        for j in range(len(A[i])):
            item = A[i][j]
            if item == 'None':
                item = None
            elif item == 'nan':
                item = None
            elif item == '':
                item = None
            elif item != item:
                item = None
            elif item == 'NaT':
                item = None
            v[i].append(item)
        v[i] = tuple(v[i])
    v = tuple(v)
    cursor.executemany(SQL, v)
    db.commit()

    if INSERT_NEW:
        INSERT_RAW_DATA(df_new, database, table)

    cursor.close()
    db.close()


def UpdateSQL2(df, database, table):
    """写入并更新数据库

    参数:
    df -- DataFrame格式数据
    database -- 数据库名称
    table -- 数据表名称
    """

    db = pymysql.connect(host=SERVER_ADDRESS,
                         user=SERVER_USER,
                         password=SERVER_PASSWORD,
                         database=database)
    cursor = db.cursor()

    cursor.execute('describe `%s`.`%s`' % (database, table))
    res = cursor.fetchall()
    col = list(pd.DataFrame(cursor.description)[0])
    COLUMNs = list(pd.DataFrame(res, columns=col)['Field'])
    df = df[[i for i in df.columns if i in COLUMNs]]

    col = df.columns
    df = df.applymap(lambda x: None if x == '' else x)
    df = df.astype(str)

    variables = ''
    values = '('
    for i in range(len(col)):
        variables += '`%s`' % col[i]
        values += '%s'
        if i != len(col)-1:
            variables += ','
            values += ','
        else:
            values += ')'

    v = []
    A = tuple(df.itertuples(index=False, name=None))
    for i in range(len(A)):
        v.append([])
        for j in range(len(A[i])):
            item = A[i][j]
            if item == 'None':
                item = None
            elif item == 'nan':
                item = None
            elif item == '':
                item = None
            elif item != item:
                item = None
            elif item == 'NaT':
                item = None
            v[i].append(item)
        v[i] = tuple(v[i])
    v = tuple(v)

    extra = ''
    for i in range(len(col)):
        extra += '`%s`=VALUES(`%s`)' % (col[i], col[i])
        if i != len(col)-1:
            extra += ','
    SQL = "INSERT INTO `%s`.`%s`(%s) VALUES %s ON DUPLICATE KEY UPDATE %s" \
        % (database, table, variables, values, extra)
    cursor.executemany(SQL, v)
    db.commit()
    cursor.close()
    db.close()


def Add_Col(database, table, Columns=None):
    """
    在数据表中添加新列

    参数:
    database -- 数据库名称
    table -- 数据表名称
    Columns -- list,需要添加的列名
    """

    db = pymysql.connect(host=SERVER_ADDRESS,
                         user=SERVER_USER,
                         password=SERVER_PASSWORD,
                         database=database)
    cursor = db.cursor()

    cursor.execute("SHOW COLUMNS FROM `%s`.`%s`" % (database, table))
    res = cursor.fetchall()
    Old_Columns = [res[i][0] for i in range(len(res))]

    New_Columns = [i for i in Columns if i not in Old_Columns]

    if len(New_Columns) != 0:
        SQL = "ALTER TABLE `%s`.`%s` " % (database, table)
        SQL = SQL + \
            "ADD COLUMN `%s` FLOAT NULL AFTER `%s`" % (
                New_Columns[0], Old_Columns[-1])
        for i in range(1, len(New_Columns)):
            SQL = SQL + ','
            SQL = SQL + \
                "ADD COLUMN `%s` FLOAT NULL AFTER `%s`" % (
                    New_Columns[i], New_Columns[i - 1])
            if i == len(New_Columns) - 1:
                SQL = SQL + ';'
        try:
            cursor.execute(SQL)
            db.commit()
        except(Exception):
            db.rollback()
            print('func error: Add_col.')

    cursor.close()
    db.close()


def Delete_Row(database, table, Row_name='基金代码', Rows=None):
    """
    删除数据表行

    参数:
    database -- 数据库名称
    table -- 数据表名称
    Rows -- list,需要删除的行索引值
    """

    db = pymysql.connect(host=SERVER_ADDRESS,
                         user=SERVER_USER,
                         password=SERVER_PASSWORD,
                         database=database)
    cursor = db.cursor()

    if Rows is None:
        Rows = list(SQL2df(database, table)[Row_name])
    for i in range(len(Rows)):
        SQL = "DELETE FROM `%s`.`%s` WHERE (`%s` = '%s');" % (
            database, table, Row_name, Rows[i])
        cursor.execute(SQL)

    db.commit()

    cursor.close()
    db.close()


def initialize_table(database, table):
    """
    删除数据表中所有数据.

    参数:
    database -- 数据库名称
    table -- 数据表名称
    """
    db = pymysql.connect(host=SERVER_ADDRESS,
                         user=SERVER_USER,
                         password=SERVER_PASSWORD,
                         database=database)
    cursor = db.cursor()
    SQL = "DELETE FROM `%s`.`%s`;" % (database, table)
    cursor.execute(SQL)
    db.commit()
    cursor.close()
    db.close()


if __name__ == '__main__':

    pass
