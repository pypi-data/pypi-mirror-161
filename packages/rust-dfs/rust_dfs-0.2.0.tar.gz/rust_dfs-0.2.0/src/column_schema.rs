use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::hash::Hash;

use crate::logical_types::LogicalTypes;

#[pyclass]
#[derive(Debug, PartialEq, Eq, Deserialize, Serialize, Clone, Copy, Hash)]
pub struct ColumnSchema {
    pub logical_type: LogicalTypes,
    pub semantic_tag: LogicalTypes,
}

impl ColumnSchema {
    pub fn new(logical_type: LogicalTypes, semantic_tag: LogicalTypes) -> ColumnSchema {
        ColumnSchema {
            logical_type,
            semantic_tag,
        }
    }
}

#[pymethods]
impl ColumnSchema {
    #[new]
    pub fn __init__(lt: Option<&str>, st: Option<&str>) -> Self {
        ColumnSchema {
            logical_type: match lt {
                Some(lt) => LogicalTypes::try_from(lt)
                    .expect(format!("{} is not a valid logical type", lt).as_str()),

                None => LogicalTypes::Unknown,
            },
            semantic_tag: match st {
                Some(lt) => LogicalTypes::try_from(lt)
                    .expect(format!("{} is not a valid logical type", lt).as_str()),
                None => LogicalTypes::Unknown,
            },
        }
    }
    fn __str__(&self) -> PyResult<String> {
        Ok(format!("{:?}:{:?}", self.logical_type, self.semantic_tag))
    }
    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}:{:?}", self.logical_type, self.semantic_tag))
    }
}

// impl PartialEq for ColumnSchema {
//     fn eq(&self, other: &Self) -> bool {
//         let lt = match (self.logical_type, other.logical_type) {
//             (LogicalTypes::Any, _) => true,
//             (_, LogicalTypes::Any) => true,
//             (a, b) => a == b,
//         };

//         let st = match (self.semantic_tag, other.semantic_tag) {
//             (LogicalTypes::Any, _) => true,
//             (_, LogicalTypes::Any) => true,
//             (a, b) => a == b,
//         };

//         lt && st
//     }
// }

#[macro_export]
macro_rules! column_schema {
    ($lt:expr, $st:expr) => {{
        use $crate::column_schema::ColumnSchema;
        use $crate::logical_types::LogicalTypes;

        let lt = LogicalTypes::try_from($lt).unwrap_or(LogicalTypes::Unknown);
        let st = LogicalTypes::try_from($st).unwrap_or(LogicalTypes::Unknown);

        ColumnSchema::new(lt, st)
    }};
}

#[cfg(test)]
mod tests {
    #[test]
    fn test_macro() {
        let b = column_schema!["integer", "numeric"];

        println!("{:?}", b);
    }
}
