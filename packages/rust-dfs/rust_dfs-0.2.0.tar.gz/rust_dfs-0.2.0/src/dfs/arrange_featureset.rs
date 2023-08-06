use std::collections::HashMap;

use crate::{column_schema::ColumnSchema, feature::Feature};

pub fn arrange_featureset(
    featureset: Vec<(ColumnSchema, Feature)>,
    index_by_schema: &HashMap<ColumnSchema, Vec<usize>>,
) -> Vec<Feature> {
    let mut current_index_by_logical_type: HashMap<ColumnSchema, usize> = HashMap::new();

    let mut features_with_position: Vec<(usize, Feature)> = Vec::new();
    for (schema, f) in featureset {
        let s = schema.clone();
        let idx = current_index_by_logical_type.entry(schema).or_insert(0);
        let idx2 = index_by_schema
            .get(&s)
            .expect(format!("Error unwrapping A {:?}", s.clone()).as_str())
            .get(*idx)
            .expect(format!("Error unwrapping B {:?} {:?}", s.clone(), index_by_schema).as_str());
        *idx += 1;

        features_with_position.push((*idx2, f));
    }

    features_with_position.sort_by(|a, b| a.0.cmp(&b.0));

    let a = features_with_position
        .iter()
        .map(|(_, f)| f)
        .cloned()
        .collect();

    return a;
}

#[cfg(test)]
mod tests {
    #[test]
    fn test_arrange_featureset2() {}
}
