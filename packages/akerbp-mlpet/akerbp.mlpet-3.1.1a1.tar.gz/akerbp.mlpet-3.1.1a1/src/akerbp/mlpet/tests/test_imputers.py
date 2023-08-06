from akerbp.mlpet.imputers import (
    generate_imputation_models,
    impute_depth_trend,
    iterative_impute,
    simple_impute,
)
from akerbp.mlpet.tests.data.data import TEST_DF


def test_simple_impute():
    df, _ = simple_impute(TEST_DF[["AC", "BS"]])
    assert not df.isnull().any().any()


def test_iterative_impute():
    df = iterative_impute(TEST_DF[["AC", "BS"]])
    assert not df.isnull().any().any()


def test_impute_depth_trend():
    df, _ = impute_depth_trend(
        TEST_DF[["DEPTH", "AC", "BS"]],
        curves_to_impute=["BS"],
        depth_column="DEPTH",
    )
    assert not df.isnull().any().any()


def test_impute_depth_trend_with_provided_models():
    models = generate_imputation_models(
        TEST_DF[["DEPTH", "AC", "BS"]], curves=["BS"], depth_column="DEPTH"
    )
    df, _ = impute_depth_trend(
        TEST_DF[["DEPTH", "AC", "BS"]],
        curves_to_impute=["BS"],
        imputation_models=models,
        depth_column="DEPTH",
    )
    assert not df.isnull().any().any()
