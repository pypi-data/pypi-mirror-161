use std::collections::HashMap;

use crate::{column_schema::ColumnSchema, input_set::InputSet, logical_types::LogicalTypes};

pub fn index_input_set(input_set: &InputSet) -> HashMap<ColumnSchema, Vec<usize>> {
    let mut inputset_by_type: HashMap<ColumnSchema, Vec<usize>> = HashMap::new();

    for (i, schema) in input_set.iter().enumerate() {
        // let lt = if input.logical_type.is_some() {
        //     let a = input.logical_type.as_ref().unwrap();
        //     a
        // } else if input.semantic_tag.is_some() {
        //     let a = input.semantic_tag.as_ref().unwrap();
        //     a
        // } else {
        //     &LogicalTypes::Any
        // };

        let index_array_for_type = inputset_by_type.entry(schema.clone()).or_insert(Vec::new());

        index_array_for_type.push(i);
    }
    return inputset_by_type;
}

#[cfg(test)]
mod tests {
    use std::{collections::HashMap, vec};

    use crate::{column_schema, input_set::InputSet, logical_types::LogicalTypes};

    use super::index_input_set;

    #[test]
    fn happy_path() {
        let c1 = column_schema!("boolean", "");
        let c2 = column_schema!("integer", "");
        let c3 = column_schema!("boolean", "");

        let input_set = InputSet::new(vec![c1.clone(), c2.clone(), c3.clone()]);

        let expected = HashMap::from([(c1.clone(), vec![0, 2]), (c2.clone(), vec![1])]);

        let actual = index_input_set(&input_set);

        assert_eq!(expected, actual);
    }
}
