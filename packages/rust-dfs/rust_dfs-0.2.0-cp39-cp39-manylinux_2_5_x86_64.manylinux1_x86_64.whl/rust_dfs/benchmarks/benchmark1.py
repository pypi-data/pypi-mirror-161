# Import Featuretools, rust_dfs, and some other utility functions
import featuretools as ft
import rust_dfs
from rust_dfs.utils import *
import time
import pandas as pd
from datetime import date


def run(nrows, ncols):
    # Generate a fake dataset with 2 Integer columns
    df = generate_fake_dataframe(
        n_rows=nrows,
        col_defs=[
            ("Integer", ncols),
            # ("Boolean", 2),
        ],
    )

    f_primitives = list(ft.primitives.utils.get_transform_primitives().values())  # type: ignore

    # convert datafame to an entityset
    es = df_to_es(df)

    # convert featuretools primitives to rust primitives
    r_primitives = convert_primitives(f_primitives)

    # convert dataframe to rust features
    r_features = dataframe_to_features(es.dataframes[0])

    # run dfs with features_only=True
    start_time = time.time()
    ft_feats = ft.dfs(
        entityset=es,
        target_dataframe_name="nums",
        trans_primitives=f_primitives,
        features_only=True,
        max_depth=1,
    )
    ft_duration = time.time() - start_time

    # Convert back into a format that we can use to compare with rust
    c_feats = convert_features(ft_feats)

    # generate engineered features using Rust
    start_time = time.time()
    r_derived_feats = rust_dfs.generate_features(r_features, r_primitives)
    rust_duration = time.time() - start_time

    return (ft_duration, rust_duration)


def main():
    nrows_list = [10, 100, 1000]
    ncols_list = [10, 100, 1000]

    out = []
    for nrows in nrows_list:
        for ncols in ncols_list:
            times = run(nrows, ncols)
            out.append(
                {
                    "nrows": nrows,
                    "ncols": ncols,
                    "ft_duration": times[0],
                    "rust_duration": times[1],
                }
            )


    results = pd.DataFrame(out)
    date_str = date.today().strftime("%Y_%m_%d")
    fname = f"data/benchmark-{date_str}.csv"
    results.to_csv(fname)


if __name__ == "__main__":
    main()
