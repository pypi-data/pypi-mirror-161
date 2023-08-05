import math

import numpy as np
import pandas as pd

from pandas._libs.lib import is_integer
from pandas.api.types import is_numeric_dtype, is_string_dtype, is_datetime64_any_dtype, is_bool_dtype

from bokeh.layouts import column, row
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LinearAxis, Range1d, HoverTool
from bokeh.models.widgets import DataTable, TableColumn, Div

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold


def target_info(df, attr, target):
    sr = df[attr].copy(deep=True)
    target_col = df[target].copy(deep=True)


    bucketed = bucketing(sr, target_col)
    cate = False
    if isinstance(bucketed, tuple):
        bucketed, bucket_table = bucketed
        cate = True

    # transform target column
    # if bool -> to int
    # and then to string
    if is_bool_dtype(target_col):
        target_col = target_col.astype(int)
    target_col = target_col.astype(str)

    # calc woe en iv
    crosstab = woe_iv(bucketed, target_col)

    # if we have perfect predictor, woe and IV will be (-) inf
    # When bokeh uses Json serialize which cant deal with infinite values
    # as such, inf are replaced by string counterparts
    if (crosstab == np.inf).any(axis=None) or (crosstab == (-np.inf)).any(axis=None):
        crosstab = crosstab.replace({np.inf: 'inf', -np.inf: '-inf'})
        return row(woe_table(crosstab))

    # calc gini
    gini = calculate_gini(bucketed, target_col)
    crosstab['gini'] = gini

    # make plot from calculations
    woe_fig = woe_plot(crosstab)

    # make table from calculations
    woe_tab = woe_table(crosstab)

    second_col = column(woe_tab, bucket_table) if cate else woe_tab

    #
    # iv_interpretation = iv_information_table()

    return row(woe_fig, second_col)


def bucketing(sr, target_col):
    if is_numeric_dtype(sr) or is_datetime64_any_dtype(sr):
        bucketed = bucketing_numeric(sr, target_col)
    elif is_string_dtype(sr):
        bucketed = bucketing_categorical(sr, target_col)
    else:
        raise TypeError
    return bucketed



def bucketing_numeric(sr, target_col):
    vc = sr.value_counts(normalize=True)
    n_unique = len(vc)

    if n_unique < 5:
        return bucketing_categorical(sr, target_col)

    vc_0 = (vc.reset_index()
                .rename(columns={'index': sr.name,
                                 sr.name: 'perc'})
                .loc[0, :])

    if vc_0['perc'] > 0.50:
        value = vc_0[sr.name]

        conditions = [sr < value,
                      sr > value]
        values = [1,3]
        bucketed = np.select(conditions, values, default=2)

        return pd.Series(bucketed, name='Bucketed')

    # N = len(sr)
    # n_null = sum(sr.isnull())

    # if missing are less then 2%, remove them
    # else give own bucket
    # if n_null < N * 0.02:
    #     df = df.query(f"{attr}.notna()", engine='python')
    #     categories = pd.qcut(df[attr],
    #                          3,
    #                          duplicates='drop',
    #                          precision=2)
    # else:
    bucketed = pd.qcut(sr,
                         3,
                         duplicates='drop',
                         precision=2)

    bucketed = bucketed.cat.add_categories('Missing').fillna('Missing')
    bucketed.name = 'Bucketed'

    return bucketed


def bucketing_categorical(sr, target_col):
    n_unique = sr.unique()
    if len(n_unique) < 5:
        return sr.rename('Bucketed')

    # cure rate per group
    df_target = pd.concat([sr, target_col], axis=1)
    grouped_dr = (df_target.groupby(sr.name, dropna=False)
                           .agg(target_rate=(target_col.name, 'mean'),
                                group_size=(target_col.name, 'count')))

    # weighed qcut approach
    grouped_dr['weighted_qcut'] = weighted_qcut(grouped_dr.target_rate,
                                                grouped_dr.group_size,
                                                q=3,
                                                labels=False)

    buckets_dict = grouped_dr['weighted_qcut'].to_dict()
    bucketed = sr.replace(buckets_dict)
    bucketed.name = 'Bucketed'

    bucket_table = bucketing_table(grouped_dr)

    # algorithm approach
    # categories2 = bucketing_algorithm_targetrate(grouped_dr, df, target, attr)

    return bucketed, bucket_table

def bucketing_table(grouped_dr):
    attr_name = grouped_dr.index.name
    df_bucket = (grouped_dr.reset_index()
                           .groupby('weighted_qcut')
                           [attr_name]
                           .agg(lambda x: ",".join(list(x.astype(str))))
                           .to_frame()
                           .reset_index()
                           .rename(columns={'weighted_qcut': 'bin'}))

    src = ColumnDataSource(df_bucket)
    table_columns = [TableColumn(field=c, title=c, width=1) for c in df_bucket.columns]
    bucket_table = DataTable(source=src,
                                        columns=table_columns,
                                        index_position=None,
                                        width=350, height=180,
                                        autosize_mode='fit_columns'
                                        )
    return bucket_table


# def bucketing_algorithm_targetrate(grouped_dr, df, target, attr):
#     '''
#     eigenlijk zou algoritme anders moeten, dat je attribuut values 1 voor 1 verschuift van bucket.
#     want gemiddelde kan nu rare sprongen maken. ook zou je in onderstaande appraoch eigenlijk
#     een value de 'kans' moeten geven om terug te gaan naar bucket 2.
#
#     Also has error which gives INF result
#     '''
#
#     # onderstaande is voor approach dat voorbij weighted q33 en q67 moet voor bucket changing.
#     # this does not make sense
#     #     grouped_dr2 = grouped_dr.sort_values('target_rate')
#     #     grouped_dr2
#     #     v= grouped_dr2['weighted_qcut'].values
#     #     idx = v[:-1] != v[1:]
#     #     q33, q67 = grouped_dr2.target_rate.iloc[np.where(idx)].values
#
#     mean = df[target].mean()
#     delta_migration_rate = 0.2 * min(mean, 1 - mean)
#
#     pdf2 = grouped_dr.copy(deep=True)
#     N = len(pdf2)
#
#     n_migration_cutoff = max(0.05 * N, 5 / mean)
#     pdf3 = pdf2.assign(Bucket=2).assign(canMigrateGroupSize=lambda x: x.group_size > n_migration_cutoff)
#
#     changes = True
#     i = 1
#     while changes:
#         print(i)
#         bucket2 = pdf3.query("Bucket == 2")
#         average_cure_rate_2 = (bucket2.target_rate * bucket2.group_size).sum() / (bucket2.group_size).sum()
#
#         pdf3['averageCureInBucket2'] = average_cure_rate_2
#
#         conditions = [pdf3.canMigrateGroupSize.values
#                       & ((pdf3.target_rate.values - pdf3.averageCureInBucket2.values) > delta_migration_rate),
#
#                       pdf3.canMigrateGroupSize.values
#                       & ((pdf3.target_rate.values - pdf3.averageCureInBucket2.values) < (-1 * delta_migration_rate))]
#
#         values = [3, 1]
#
#         pdf3['BucketNew'] = np.select(conditions, values, default=2)
#
#         changes = sum(pdf3.BucketNew != pdf3.Bucket)
#
#         pdf3['Bucket'] = pdf3['BucketNew']
#
#         i += 1
#
#
#     bucket_mapping = pdf3['BucketNew'].to_dict()
#     categories = df[attr].replace(bucket_mapping)
#
#     return categories


def weighted_qcut(values, weights, q, **kwargs):
    'Return weighted quantile cuts from a given series, values.'

    '''
    from https://stackoverflow.com/questions/45528029/python-how-to-create-weighted-quantiles-in-pandas
    '''
    if is_integer(q):
        quantiles = np.linspace(0, 1, q + 1)
    else:
        quantiles = q
    order = weights.iloc[values.argsort()].cumsum()
    returned = pd.cut(order / order.iloc[-1], quantiles, **kwargs)

    if 'retbins' in kwargs:
        if kwargs['retbins']:
            return (returned[0].sort_index(), returned[1])
    else:
        return returned.sort_index()


def woe_iv(bucketed, target):
    crosstab = pd.crosstab(bucketed,
                           target)

    crosstab.columns = crosstab.columns.astype(str)
    for c in crosstab.columns:
        crosstab[c + '_normalized'] = crosstab[c] / sum(crosstab[c])

    crosstab = crosstab.assign(target_rate=lambda x: x['1'] / (x['1'] + x['0'])) \
        .assign(woe=lambda dfx: np.log(dfx['1_normalized'] / dfx['0_normalized'])) \
        .assign(iv=lambda dfx: np.sum(dfx['woe'] * (dfx['1_normalized'] - dfx['0_normalized'])))
    crosstab.columns.name = None
    crosstab.index = crosstab.index.astype(str)
    crosstab = crosstab.drop(['0_normalized', '1_normalized'], axis='columns')



    return crosstab


def woe_plot(crosstab):
    p = figure(x_range=crosstab.index.to_list(), width=400, height=300, toolbar_location=None, title='WOE binning')

    colors = ["#718dbf", "#e84d60"]

    src = ColumnDataSource(crosstab)

    renderers = p.vbar_stack(['0', '1'],
                             width=0.7,
                             x='Bucketed',
                             source=src,
                             color=colors)

    # y_axis Woe
    woe_min = crosstab.woe.min()
    woe_max = crosstab.woe.max()

    p.extra_y_ranges = {"woe_range": Range1d(start=woe_min * 1.2, end=woe_max * 1.2)}
    p.add_layout(LinearAxis(y_range_name="woe_range"), 'right')

    p.line(x='Bucketed',
           y='woe',
           source=src,
           y_range_name='woe_range',
           color='lightgreen',
           width=3,
           legend_label='WOE')
    p.x_range.range_padding = 0
    p.title.align = 'center'

    for r in renderers:
        outcome = r.name
        hover = HoverTool(tooltips=[
            (f"{outcome} ", f"@{outcome}")
        ], renderers=[r])
        p.add_tools(hover)

    return p


def calculate_gini(categories,target_col):
    categories_dummies = pd.get_dummies(categories, drop_first=True)
    k = 5
    kf = KFold(n_splits=k, random_state=None)
    model = LogisticRegression(solver='liblinear')

    result = cross_val_score(model, categories_dummies.values, target_col, cv=kf, scoring='roc_auc')
    gini = (2 * result - 1).mean()

    return gini

def woe_table(crosstab):
    n_digits = 2



    def round_to_n_digits(x):
        return round(x, n_digits - int(math.floor(math.log10(abs(x)))) - 1) if x else x

    def my_round(x):
        return round(x) if abs(x) > (10 ** (n_digits - 1)) else round_to_n_digits(x)

    def my_format(x):
        return f"{my_round(x):,}" if np.isfinite(x) else x

    crosstab2 = crosstab.copy(deep=True).reset_index()
    for c in crosstab2.columns:
        if is_numeric_dtype(crosstab2[c]):
            crosstab2[c] = crosstab2[c].map(my_format)

    src = ColumnDataSource(crosstab2)


    # width = 1 is required to solve bug in
    # autosize_mode = 'fit_columns'. Some columns
    # will not render if width = 1 is not specified.
    table_columns = [TableColumn(field=c, title=c, width=1) for c in crosstab2.columns]
    woe_table = DataTable(source=src,
                            columns=table_columns,
                            index_position=None,
                            width=350, height=180,
                              autosize_mode='fit_columns'
                         )


    table_title = Div(text=""" 
         &nbsp; &nbsp;  <b>Bucketing, WOE, IV and GINI </b> 
          """,
              width=300, height=30)
    return column(table_title, woe_table)


def iv_information_table():
    iv_interpretation = pd.DataFrame({'IV': ['<0.02',
                                             '0.02 to 0.1',
                                             '0.1 to 0.3',
                                             '0.3 to 0.5',
                                             '> 0.5'],
                                      'Interpretation': ['No predictive power',
                                                         'Weak predictive power',
                                                         'Medium predictive power',
                                                         'Strong predictive power',
                                                         'Suspicious']})
    src = ColumnDataSource(iv_interpretation)
    table_columns = [TableColumn(field=c, title=c, width=1) for c in iv_interpretation.columns]
    iv_interpretation_table = DataTable(source=src,
                                        columns=table_columns,
                                        index_position=None,
                                        width=200, height=180,
                                        autosize_mode='fit_columns'
                                        )
    return iv_interpretation_table
