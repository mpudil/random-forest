import pytest
import numpy as np
import pandas as pd
import sql_tree as st
import credentials as cd
import classification_tree as ct


# Predictions from sql and Python same 
# Random data generated by:
    # x_df = pd.DataFrame(np.random.randn(15, 3), columns=range(3))
    # y_df = pd.DataFrame(np.random.randint(0, 2, size=(15,1)), columns=['y'])

def test_sql_python_same():
    cur = st.sqlconnect(host = cd.host, database = cd.database, user=cd.user, password = cd.password)
    x_df = pd.DataFrame([[1.35090528, -0.22763714,  0.62503887],
    [-0.0715539 , -0.64119863, -0.19062135],
    [-1.11177092,  0.50165846, -0.86722735],
    [ 1.24392279, -0.08266315, -0.82700858],
    [ 0.41391078, -1.06708343, -0.591038  ],
    [-0.11328491,  2.19414569, -1.0890808 ],
    [ 1.00572935, -0.92290436,  1.38861161],
    [-0.78596497,  1.56025647,  0.95610325],
    [ 1.59251311,  2.18732072, -0.73577758],
    [-1.16918551, -0.21258418,  1.27649019],
    [ 0.70237481,  1.82188747, -0.04181062],
    [-0.56060812,  0.56029165, -0.90909157],
    [ 0.44574311,  0.94814604, -0.01507905],
    [-1.3072048 ,  1.62805262, -0.56249722],
    [ 0.62097551, -1.33599419,  0.1845642 ]], columns = ['v1', 'v2', 'v3'])

    y_df = pd.DataFrame([[1], [0], [0], [1], [0], [0], [1], [0], [1], [0], [0], [1], [0], [1], [0]], columns=['y'])

    tree_ct = ct.DecisionTree(x_df, y_df)

    x_test = pd.DataFrame([[ 0.31269028,  1.86935075,  1.3147904],
    [ 1.47276502, -1.77782668, -0.36375857],
    [ 1.59640162, -1.21098536, -0.07769382],
    [-0.40091173, -0.7496455 ,  0.39000357],
    [-0.29370055, -0.40686242,  1.44866448],
    [ 0.06426318, -1.30074211,  0.49274947],
    [ 0.16542666,  0.61140155, -1.94330865]], columns = ['v1', 'v2', 'v3'])

    tree_ct_preds = tree_ct.predict(x_test)
    tree_preds_df = pd.concat([x_test, pd.DataFrame([int(p) for p in tree_ct_preds], columns=['preds'])], axis=1).sort_values('v1')
    tree_preds_df.index = range(tree_preds_df.shape[0])

    cur.execute("CREATE TABLE IF NOT EXISTS datatable (v1 FLOAT, v2 FLOAT, v3 FLOAT, y INT);")
    cur.execute("DELETE FROM datatable;")

    a = "INSERT INTO datatable (v1, v2, v3, y) VALUES (1.35090528, -0.22763714,  0.62503887, 1), " 
    b = "(-0.0715539 , -0.64119863, -0.19062135, 0), (-1.11177092,  0.50165846, -0.86722735, 0)," 
    c = "(1.24392279, -0.08266315, -0.82700858, 1), (0.41391078, -1.06708343, -0.591038, 0)," 
    d = "(-0.11328491,  2.19414569, -1.0890808, 0),(1.00572935, -0.92290436,  1.38861161, 1)," 
    e = "(-0.78596497,  1.56025647,  0.95610325, 0),(1.59251311,  2.18732072, -0.73577758, 1)," 
    f = "(-1.16918551, -0.21258418,  1.27649019, 0),(0.70237481,  1.82188747, -0.04181062, 0)," 
    g = "(-0.56060812,  0.56029165, -0.90909157, 1), (0.44574311,  0.94814604, -0.01507905, 0)," 
    h = "(-1.3072048 ,  1.62805262, -0.56249722, 1),(0.62097551, -1.33599419,  0.1845642, 0);"
    query_data = a + b + c + d + e + f + g + h
    cur.execute(query_data)
    tree_st = st.SQLTree("datatable", ['v1', 'v2', 'v3'], 'y', cur)
    cur.execute("CREATE TABLE IF NOT EXISTS testtable (v1 FLOAT, v2 FLOAT, v3 FLOAT);")
    cur.execute("DELETE FROM testtable;")

    i = "INSERT INTO testtable (v1, v2, v3) VALUES (0.31269028,  1.86935075,  1.3147904), "
    j = "(1.47276502, -1.77782668, -0.36375857), (1.59640162, -1.21098536, -0.07769382), "
    k = "(-0.40091173, -0.7496455, 0.39000357), (-0.29370055, -0.40686242,  1.44866448), "
    l = "(0.06426318, -1.30074211,  0.49274947), (0.16542666,  0.61140155, -1.94330865);"
    query_test = i + j + k + l
    cur.execute(query_test) 
    tree_st.predict("testtable")
    cur.execute("SELECT * FROM testtable;")
    preds_sql = cur.fetchall()
    preds_df_sql = pd.DataFrame(preds_sql, columns=['v1', 'v2', 'v3', 'preds']).sort_values('v1')
    preds_df_sql.index = range(preds_df_sql.shape[0])

    assert tree_preds_df.equals(preds_df_sql)


    # We should also get the same results if we prune at the same level
    tree_ct.prune(alphas=[0.2], cross_validate=False)
    tree_st.prune(alpha=0.2)
  

    # Python preds, pruned
    tree_ct_preds_pruned = tree_ct.predict(x_test)
    tree_preds_df_pruned = pd.concat([x_test, pd.DataFrame([int(p) for p in tree_ct_preds_pruned], columns=['preds'])], axis=1).sort_values('v1')
    tree_preds_df_pruned.index = range(tree_preds_df_pruned.shape[0])

    # SQL preds, pruned
    cur.execute("ALTER TABLE testtable DROP COLUMN preds;")
    tree_st.predict("testtable")
    cur.execute("SELECT * FROM testtable;")
    preds_sql_pruned = cur.fetchall()
    preds_df_sql_pruned = pd.DataFrame(preds_sql_pruned, columns=['v1', 'v2', 'v3', 'preds']).sort_values('v1')
    preds_df_sql_pruned.index = range(preds_df_sql_pruned.shape[0])

    assert tree_preds_df_pruned.equals(preds_df_sql_pruned)
    

# get_data_in_region test
def test_get_data_sql():
        cur = st.sqlconnect(host = cd.host, database = cd.database, user=cd.user, password = cd.password)
        cur.execute("CREATE TABLE IF NOT EXISTS datatosub (v1 FLOAT, v2 FLOAT, y INT);")
        cur.execute("DELETE FROM datatosub;")
        cur.execute("INSERT INTO datatosub (v1, v2, y) VALUES (1, 2, 1), (0, 3, 0), (2,-1, 1), (5, -1, 1);")
        path = ['v1 > 0', 'v2 <= 4']
        subset_data_sql = st.get_data_in_region("datatosub", cur, path, fetch=True)
        subset_data_sql_df = pd.DataFrame(subset_data_sql, columns = ['v1', 'v2', 'y']).sort_values('v1')
        subset_data_sql_df.index = range(subset_data_sql_df.shape[0])

        # Make sure this matches the subset version in the classification_tree module
        x_df = pd.DataFrame([[1, 2], [0, 3], [2, -1], [5, -1]], columns=['v1', 'v2'])
        y_df = pd.DataFrame([[1], [0], [1], [1]], columns=['y'])
        subset_x, subset_y = ct.get_data_in_region(x_df, y_df, path)
        subset_data_pandas = pd.concat([subset_x, subset_y], axis=1)
        subset_data_pandas.index = range(subset_data_pandas.shape[0])
        
        assert subset_data_pandas.astype(int).equals(subset_data_sql_df.astype(int))



@pytest.fixture
def sql_r2_tree_basic():
    cur = st.sqlconnect(host = cd.host, database = cd.database, user=cd.user, password = cd.password)
    
    cur.execute("CREATE TABLE IF NOT EXISTS data1 (v1 FLOAT, v2 FLOAT, y INT);")
    cur.execute("DELETE FROM data1;")
    cur.execute("INSERT INTO data1 (v1, v2, y) VALUES (1.5,5,0), (4,2,0), (1,1,0), (2,4,0), (3.5,1,0), (-1.2,6,1), (-2,9,1), (-5,1,1), (-7,1,1), (-6,4,1), (-4,-5,0), (-1,-2,0), (-0.2,-5,0), (5,-1,1);")
    sqlt = st.SQLTree("data1", ["v1", "v2"], "y", cur)

    return cur, sqlt


def test_sql_same_paths(sql_r2_tree_basic):
    # This should match the output from the Pandas dataframe since we are 
    # using the same process and data!!
    _, sqlt = sql_r2_tree_basic
    assert sqlt.tnode.lhs.path == ['v1 <= -1.2']
    assert sqlt.tnode.rhs.path == ['v1 > -1.2']


def test_100_accuracy_train_unpruned(sql_r2_tree_basic):
    cur, sqlt = sql_r2_tree_basic
    # Put data (actual) in dataframe and sort by v1
    cur.execute("SELECT * FROM data1;")
    data = pd.DataFrame(cur.fetchall(), columns = ['v1', 'v2', 'y'])
    data = data.sort_values('v1')
    data.index = range(data.shape[0])

    # Copy data to use as "test" dataset
    cur.execute("CREATE TABLE IF NOT EXISTS datacopy AS SELECT v1, v2 FROM data1;")

    # Make predictions (overfitting should lead to this beinng 1)
    sqlt.predict("datacopy") 

    # Put predictions in sorted dataframe and sort by v1 
    cur.execute("SELECT * FROM datacopy;")
    datapred = pd.DataFrame(cur.fetchall(), columns = ['v1', 'v2', 'y'])
    datapred = datapred.sort_values('v1')
    datapred.index = range(datapred.shape[0])
    assert all(datapred == data) # Should be same as input


@pytest.fixture   
def sql_r3_tree():
    cur = st.sqlconnect(host = cd.host, database = cd.database, user=cd.user, password = cd.password)
    cur.execute("CREATE TABLE IF NOT EXISTS datar3 (v1 FLOAT, v2 FLOAT, v3 FLOAT, y INT);")
    cur.execute("DELETE FROM datar3;")
    cur.execute("INSERT INTO datar3 (v1, v2, v3, y) VALUES (0.3, 2.5, 1.79, 1), (2.9, 2.8, 7.1, 1),(2.1, 7.1, 3, 0), (1.1, 18.1, 0.2, 0), (5.1, 6.1, -1, 1), (3.1, -2.8, -3.1, 1), (5.1, 1.1, 1.09, 0), (4.8, -4.1, 0.5, 0)")
    sqlt = st.SQLTree("datar3", ["v1", "v2", "v3"], "y", cur)
    return cur, sqlt



