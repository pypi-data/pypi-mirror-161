pub mod column_schema;
pub mod dfs;
pub mod feature;
pub mod input_set;
pub mod logical_types;
pub mod primitive;

use column_schema::ColumnSchema;
use input_set::InputSet;
use rayon::prelude::*;

use feature::{compare_featuresets, generate_fake_features as r_generate_fake_features, Feature};
use pyo3::prelude::*;

use crate::{dfs::generate_features_for_primitive, primitive::Primitive};

#[pyfunction]
fn load_primitives(filename: String) -> PyResult<Vec<Primitive>> {
    let primitives = Primitive::read_from_file(filename);
    Ok(primitives)
}

#[pyfunction]
fn generate_fake_features(n_features: i32) -> PyResult<Vec<Feature>> {
    let features = r_generate_fake_features(n_features);
    Ok(features)
}

#[pyfunction]
fn generate_features(features: Vec<Feature>, primitives: Vec<Primitive>) -> PyResult<Vec<Feature>> {
    let t1_primitives: Vec<&Primitive> = primitives
        .iter()
        .filter(|x| x.function_type == "transform")
        .collect();

    let features_ref = &features;

    let new_features: Vec<Feature> = t1_primitives
        .par_iter()
        // .iter()
        .map(|&p| generate_features_for_primitive(p, features_ref))
        .flatten()
        .collect();

    // append new feature to origin features
    let all_features: Vec<Feature> = features.into_iter().chain(new_features).collect();
    Ok(all_features)
}

/// A Python module implemented in Rust.
#[pymodule]
fn rust_dfs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(generate_features, m)?)?;
    m.add_function(wrap_pyfunction!(load_primitives, m)?)?;
    m.add_function(wrap_pyfunction!(generate_fake_features, m)?)?;
    m.add_function(wrap_pyfunction!(compare_featuresets, m)?)?;

    m.add_class::<Feature>()?;
    m.add_class::<Primitive>()?;
    m.add_class::<ColumnSchema>()?;
    m.add_class::<InputSet>()?;

    Ok(())
}
