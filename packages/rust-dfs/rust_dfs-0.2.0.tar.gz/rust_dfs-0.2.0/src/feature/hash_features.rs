use std::collections::{HashMap, HashSet};

use crate::{column_schema::ColumnSchema, logical_types::LogicalTypes};

use super::Feature;

pub fn hash_features(features: &Vec<Feature>) -> HashMap<LogicalTypes, HashSet<&Feature>> {
    let mut features_by_type: HashMap<LogicalTypes, HashSet<&Feature>> = HashMap::new();

    for feature in features {
        let logical_type = feature.schema.logical_type;

        if logical_type != LogicalTypes::Unknown {
            let features_of_type = features_by_type
                .entry(logical_type)
                .or_insert(HashSet::new());
            features_of_type.insert(feature);
        }

        let semantic_tag = feature.schema.semantic_tag;

        if semantic_tag != LogicalTypes::Unknown {
            let features_of_type = features_by_type
                .entry(semantic_tag)
                .or_insert(HashSet::new());

            features_of_type.insert(feature);
        }

        let features_of_type = features_by_type
            .entry(LogicalTypes::Any)
            .or_insert(HashSet::new());

        features_of_type.insert(feature);
    }

    return features_by_type;
}

pub fn get_matching_features(features: &Vec<Feature>, col_schema: ColumnSchema) -> Vec<Feature> {
    let hmap = hash_features(features);
    let f_by_lt = hmap
        .get(&col_schema.logical_type)
        .unwrap_or(&HashSet::new())
        .clone();
    let f_by_st = hmap
        .get(&col_schema.semantic_tag)
        .unwrap_or(&HashSet::new())
        .clone();

    let a = f_by_lt
        .intersection(&f_by_st)
        .cloned()
        .cloned()
        .collect::<Vec<_>>();

    return a;
}

#[cfg(test)]
mod tests {
    use super::Feature;
    use hash_features::get_matching_features;
    use std::collections::{HashMap, HashSet};

    use crate::{
        column_schema, create_feature, feature::hash_features, logical_types::LogicalTypes,
    };

    #[test]
    fn test_hash_features() {
        let c1 = column_schema!["double", "numeric"];
        let c2 = column_schema!["none", "numeric"];

        let f1 = create_feature!("f1", c1.clone());
        let f2 = create_feature!("f2", c2.clone());

        let fset1 = vec![f1.clone(), f2.clone()];
        let fset2 = vec![f1.clone(), f2.clone()];
        let fset3 = vec![f1.clone()];

        let s1 = HashSet::from_iter(&fset1);
        let s2 = HashSet::from_iter(&fset2);
        let s3 = HashSet::from_iter(&fset3);

        let expected = HashMap::from([
            (LogicalTypes::Any, s1),
            (LogicalTypes::Numeric, s2),
            (LogicalTypes::Double, s3),
        ]);

        let features = vec![f1.clone(), f2.clone()];

        let actual = hash_features(&features);

        assert_eq!(actual, expected);
    }

    #[test]
    fn test_get_matching_features() {
        let f1 = create_feature!("f1", column_schema!["double", "numeric"]);
        let f2 = create_feature!("f2", column_schema!["none", "numeric"]);
        let f3 = create_feature!("f3", column_schema!["double", "unknown"]);
        let f4 = create_feature!("f4", column_schema!["none", "categorical"]);
        let f5 = create_feature!("f5", column_schema!["none", "categorical"]);

        let features = vec![f1.clone(), f2.clone(), f3.clone(), f4.clone(), f5.clone()];

        let actual = get_matching_features(&features, column_schema!["any", "numeric"]);
        let s1: HashSet<Feature> = HashSet::from_iter(vec![f1.clone(), f2.clone()]);
        let s2: HashSet<Feature> = HashSet::from_iter(actual.clone());

        assert_eq!(s1, s2);

        let actual = get_matching_features(&features, column_schema!["double", "numeric"]);
        let s1: HashSet<Feature> = HashSet::from_iter(vec![f1.clone()]);
        let s2: HashSet<Feature> = HashSet::from_iter(actual.clone());

        assert_eq!(s1, s2);

        let actual = get_matching_features(&features, column_schema!["double", "any"]);
        let s1: HashSet<Feature> = HashSet::from_iter(vec![f1.clone(), f3.clone()]);
        let s2: HashSet<Feature> = HashSet::from_iter(actual.clone());

        assert_eq!(s1, s2);

        let actual = get_matching_features(&features, column_schema!["any", "any"]);
        let s1: HashSet<Feature> = HashSet::from_iter(vec![
            f1.clone(),
            f2.clone(),
            f3.clone(),
            f4.clone(),
            f5.clone(),
        ]);
        let s2: HashSet<Feature> = HashSet::from_iter(actual.clone());

        assert_eq!(s1, s2);

        let actual = get_matching_features(&features, column_schema!["any", "categorical"]);
        let s1: HashSet<Feature> = HashSet::from_iter(vec![f4.clone(), f5.clone()]);
        let s2: HashSet<Feature> = HashSet::from_iter(actual.clone());

        assert_eq!(s1, s2);

        let actual = get_matching_features(&features, column_schema!["boolean", "categorical"]);
        let s1: HashSet<Feature> = HashSet::from_iter(vec![]);
        let s2: HashSet<Feature> = HashSet::from_iter(actual.clone());

        assert_eq!(s1, s2);
    }
}
