use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

use crate::column_schema::ColumnSchema;

#[pyclass]
#[derive(Debug, PartialEq, Eq, Deserialize, Serialize, Clone, Hash)]
pub struct InputSet(pub Vec<ColumnSchema>);

// https://users.rust-lang.org/t/access-tuple-struct-with-one-element-more-ergonomically/27236/3
impl core::ops::Deref for InputSet {
    type Target = Vec<ColumnSchema>;

    fn deref(self: &'_ Self) -> &'_ Self::Target {
        &self.0
    }
}

#[pymethods]
impl InputSet {
    #[new]
    pub fn __init__(inputs: Vec<(Option<&str>, Option<&str>)>) -> Self {
        InputSet(
            inputs
                .iter()
                .map(|(lt, st)| ColumnSchema::__init__(*lt, *st))
                .collect(),
        )
    }
    fn __str__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self.0))
    }
    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self.0))
    }
}

impl InputSet {
    pub fn new(input_set: Vec<ColumnSchema>) -> InputSet {
        InputSet(input_set)
    }
}

#[macro_export]
macro_rules! input_set {
    ($($x:expr),*) => {{

        use $crate::column_schema::ColumnSchema;
        use $crate::input_set::InputSet;
        use $crate::logical_types::LogicalTypes;

        let mut inputset = vec![];
        $(
            let a = LogicalTypes::try_from($x[0]).unwrap_or(LogicalTypes::Unknown);

            let b = LogicalTypes::try_from($x[1]).unwrap_or(LogicalTypes::Unknown);

            let i = ColumnSchema::new(a, b);

            inputset.push(i);
        )*

        InputSet::new(inputset)
    }};
}

#[cfg(test)]
mod tests {

    // use crate::input_set::InputSet;
    // use crate::column_schema::ColumnSchema;
    // use crate::logical_types::LogicalTypes;

    #[test]
    fn test_macro() {
        // let b = input_set![["integer", "numeric"], ["boolean", ""]];

        // println!("{:?}", b);
    }
}
