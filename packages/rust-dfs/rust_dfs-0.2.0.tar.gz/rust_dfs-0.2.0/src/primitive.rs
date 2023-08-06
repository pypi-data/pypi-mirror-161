use pyo3::prelude::*;
use std::fmt;
use std::fs::read_to_string;

use serde::{Deserialize, Serialize};

use crate::{column_schema::ColumnSchema, input_set::InputSet};

#[pyclass]
#[derive(Debug, PartialEq, Eq, Deserialize, Serialize, Clone, Hash)]
pub struct Primitive {
    #[pyo3(get, set)]
    #[serde(alias = "type")]
    pub name: String,
    pub module: String,
    pub column_schemas: Vec<InputSet>,
    pub return_type: ColumnSchema,
    pub function_type: String,
    pub commutative: bool,
}

#[pymethods]
impl Primitive {
    #[new]
    fn __init__(
        name: &str,
        module: &str,
        function_type: &str,
        commutative: bool,
        column_schemas: Vec<Vec<(Option<&str>, Option<&str>)>>,
        return_type: (Option<&str>, Option<&str>),
    ) -> Self {
        let a = column_schemas
            .iter()
            .map(|x| InputSet::__init__(x.clone()))
            .collect();

        let b = ColumnSchema::__init__(return_type.0, return_type.1);

        Primitive {
            name: name.to_string(),
            module: module.to_string(),
            function_type: function_type.to_string(),
            commutative,
            column_schemas: a,
            return_type: b,
        }
    }
    fn __str__(&self) -> PyResult<String> {
        Ok(format!(
            "{}:{}:{}:{}:{:?}",
            self.name, self.module, self.function_type, self.commutative, self.column_schemas
        ))
    }
    fn __repr__(&self) -> PyResult<String> {
        Ok(format!(
            "{}:{}:{}:{}:{:?}",
            self.name, self.module, self.function_type, self.commutative, self.column_schemas
        ))
    }
}

impl Primitive {
    // pub fn write_to_file(&self) {
    //     let j = serde_json::to_string(self);

    //     println!("--- PRIMITIVE AS JSON");
    //     match j {
    //         Ok(s) => {
    //             println!("{}", s);
    //             let filename = format!("{}.json", self.name);
    //             let mut file = File::create(filename).unwrap();
    //             let p = format!("{}\n", s);
    //             file.write_all(p.as_bytes()).expect("Error writing to file");
    //         }
    //         Err(e) => println!("{}", e),
    //     }
    // }

    pub fn read_from_file(filename: String) -> Vec<Primitive> {
        let contents = read_to_string(filename).expect("Something went wrong reading the file");
        let primitives: Vec<Primitive> = serde_json::from_str(&contents[..]).unwrap();
        return primitives;
    }
}

impl fmt::Display for Primitive {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.name)
    }
}

impl Primitive {
    pub fn new(
        name: String,
        column_schemas: Vec<InputSet>,
        return_type: ColumnSchema,
        commutative: bool,
    ) -> Primitive {
        Primitive {
            name,
            module: "".to_string(),
            column_schemas,
            return_type,
            function_type: "transform".to_string(),
            commutative,
        }
    }
}

#[macro_export]
macro_rules! primitive {
    ($name:expr, $inputs:expr, $r_type:expr, $commutative:expr) => {{
        use $crate::primitive::Primitive;
        Primitive::new($name.to_string(), $inputs, $r_type, $commutative)
    }};
}
#[cfg(test)]
mod tests {
    use crate::column_schema;
    use crate::input_set;

    #[test]
    fn test_macro() {
        let inputs = vec![
            input_set![["", "numeric"], ["", "numeric"]],
            input_set![["datetime", ""], ["datetime", ""]],
            input_set![["ordinal", ""], ["ordinal", ""]],
        ];

        let r_type = column_schema!["integer", "numeric"];

        let p = primitive!("GreaterThan", inputs, r_type, false);
        println!("{:?}", p);
    }

    #[test]
    fn test_equality() {
        let inputs1 = vec![
            input_set![["", "numeric"], ["", "numeric"]],
            input_set![["datetime", ""], ["datetime", ""]],
            input_set![["ordinal", ""], ["ordinal", ""]],
        ];

        let r_type1 = column_schema!["integer", "numeric"];

        let p1 = primitive!("GreaterThan", inputs1, r_type1, false);

        let inputs2 = vec![
            input_set![["", "numeric"], ["", "numeric"]],
            input_set![["datetime", ""], ["datetime", ""]],
            input_set![["ordinal", ""], ["ordinal", ""]],
        ];

        let r_type2 = column_schema!["integer", "numeric"];

        let p2 = primitive!("GreaterThan", inputs2, r_type2, false);

        assert_eq!(p1, p2);
    }
}
