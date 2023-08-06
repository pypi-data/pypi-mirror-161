# content of test_sample.py
import featuretools as ft
from rust_dfs.utils import (
    generate_fake_dataframe,
    df_to_es,
    convert_features,
    convert_primitives,
    dataframe_to_features,
)
from rust_dfs import generate_features, compare_featuresets
import pytest


@pytest.mark.skip(reason="no way of currently testing this")
def test_generate_fake_dataframe():
    ncols = 5
    df = generate_fake_dataframe(
        n_rows=10,
        col_defs=[
            ("Boolean", ncols),
            ("BooleanNullable", ncols),
            ("Datetime", ncols),
            ("EmailAddress", ncols),
            ("LatLong", ncols),
            ("NaturalLanguage", ncols),
            ("Ordinal", ncols),
            ("URL", ncols),
            #
            ("Categorical", ncols),
            ("DateOfBirth", ncols),
            ("ForeignKey", ncols),
            ("Numeric", ncols),
            ("TimeIndex", ncols),
        ],
    )

    print(df)


def test_rust_dfs():
    ncols = 10
    df = generate_fake_dataframe(
        n_rows=100,
        col_defs=[
            ("Boolean", ncols),
            ("BooleanNullable", ncols),
            ("Datetime", ncols),
            ("EmailAddress", ncols),
            ("LatLong", ncols),
            ("NaturalLanguage", ncols),
            ("Ordinal", ncols),
            ("URL", ncols),
            
            ("Categorical", ncols),
            ("DateOfBirth", ncols),
            ("Numeric", ncols),

            # ("ForeignKey", ncols),
            # ("TimeIndex", ncols),
        ],
        time_index=True
    )

    # f_primitives = [
    #     ft.primitives.NumericLag,
    #     # ft.primitives.LessThan
    # ]

    f_primitives = list(ft.primitives.utils.get_transform_primitives().values())
    suspect_primitives = [
        'diff_datetime', 
        'geomidpoint', 
        'age',
    ]

    f_primitives = [x for x in f_primitives if x.name not in suspect_primitives]
    # breakpoint()

    es = df_to_es(df)

    # run dfs with features_only=True
    ft_feats = ft.dfs(
        entityset=es,
        target_dataframe_name="nums",
        trans_primitives=f_primitives,
        features_only=True,
        max_depth=1,
    )

    # ft_feats = [<Feature: F_0>, <Feature: F_1>, <Feature: F_0 > F_1>, <Feature: F_1 > F_0>]

    base_col_names = df.columns.values.tolist()

    # Convert back into a format that we can use to compare with rust
    c_feats = list(convert_features(ft_feats).values())
    c_feats = [x for x in c_feats if x.name not in base_col_names]

    # Now run using Rust

    # convert featuretools primitives to rust primitives
    r_primitives = convert_primitives(f_primitives)

    # convert dataframe to rust features
    r_features = dataframe_to_features(df)

    # generate engineered features using Rust (create new features only)
    r_derived_feats = generate_features(r_features, r_primitives)
    r_derived_feats = [x for x in r_derived_feats if x.name not in base_col_names]
    # remove index column
    # r_derived_feats = [x for x in r_derived_feats if x.name != "idx"]

    a, b = compare_featuresets(c_feats, r_derived_feats)

    assert len(a) == 0
    assert len(b) == 0
