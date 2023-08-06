use crate::{
    column_schema::ColumnSchema,
    dfs::arrange_featureset::arrange_featureset,
    feature::{get_matching_features, Feature},
    input_set::InputSet,
};
use itertools::Itertools;
use std::collections::HashMap;

use super::{generate_combinations, index_input_set};

/// Generates a vector of featuresets for a given primitive.
///
/// For example, lets represent a feature as F1::A, this is a feature
/// with the name F1 and has a logical type of A.
///
/// If the the input features set is [F1::A, F2::A, F3::B, F4::A, F5::A], and the primitive has
/// a signature of [A,B,A], the possible output featuresets are:
///
/// [
///     [F1::A, F3::B, F2::A],
///     [F1::A, F3::B, F4::A],
///     [F2::A, F3::B, F4::A],
///     [F1::A, F5::B, F2::A],
///     [F1::A, F5::B, F4::A],
///     [F2::A, F5::B, F4::A],
/// ]
///
pub fn generate_feature_sets<'a>(
    features: &'a Vec<Feature>,
    input_set: &'a InputSet,
    is_commutative: bool,
) -> Vec<Vec<Feature>> {
    let column_schema_categories: HashMap<ColumnSchema, Vec<usize>> = index_input_set(input_set);

    let csc2 = column_schema_categories.clone();

    let mut feature_combinations_for_type = Vec::new();

    for (key, value) in column_schema_categories {
        let n_inputs = value.len();
        let a = get_matching_features(features, key);
        let features_for_type = a.iter().map(|f| (key.clone(), f.clone())).collect_vec();

        let perms = generate_combinations(features_for_type, n_inputs, is_commutative);

        feature_combinations_for_type.push(perms);
    }

    let combinations_product = feature_combinations_for_type
        .iter()
        .cloned()
        .multi_cartesian_product()
        .map(|x| x.iter().flatten().cloned().collect_vec())
        .map(|x| arrange_featureset(x, &csc2))
        .collect_vec();

    return combinations_product;
}

#[cfg(test)]
mod tests {

    use std::collections::HashSet;

    use crate::{column_schema, create_feature, feature::Feature, input_set::InputSet};

    use super::generate_feature_sets;

    #[test]
    fn test_generate_feature_sets() {
        let c1 = column_schema!("boolean", "any");
        let c2 = column_schema!("any", "numeric");

        let inputset = InputSet::new(vec![c1.clone(), c2.clone(), c1.clone()]);

        let f1 = create_feature!("F1", "boolean", "categorical");
        let f2 = create_feature!("F2", "boolean", "categorical");
        let f3 = create_feature!("F3", "integer", "numeric");
        let f4 = create_feature!("F4", "boolean", "categorical");
        let f5 = create_feature!("F5", "integer", "numeric");

        let features: &Vec<Feature> =
            &vec![f1.clone(), f2.clone(), f3.clone(), f4.clone(), f5.clone()];

        let expected = HashSet::from([
            "F1_F3_F2", "F2_F3_F1", "F1_F3_F4", "F4_F3_F1", "F2_F3_F4", "F4_F3_F2", "F1_F5_F2",
            "F2_F5_F1", "F1_F5_F4", "F4_F5_F1", "F2_F5_F4", "F4_F5_F2",
        ]);

        let actual = generate_feature_sets(features, &inputset, false);

        let actual_str: Vec<String> = actual
            .iter()
            .map(|x| {
                let names: Vec<String> = x.iter().map(|x| &x.name).cloned().collect();
                return names.join("_");
            })
            .collect();

        // TODO: don't use strings
        for a in actual_str {
            assert!(expected.contains(&a[..]));
        }
    }
}
