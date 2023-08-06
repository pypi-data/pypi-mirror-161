use itertools::Itertools;

use crate::{feature::Feature, primitive::Primitive};

use super::generate_feature_sets;

pub fn generate_features_for_primitive<'a>(
    primitive: &'a Primitive,
    features: &'a Vec<Feature>,
) -> Vec<Feature> {
    // a primitive may have multiple input types, so we need to generate all the possible combinations of
    // featureset for each input type

    let mut new_features: Vec<Feature> = Vec::new();
    for inputset in &primitive.column_schemas {
        let featuresets = generate_feature_sets(features, inputset, primitive.commutative);

        for featureset in featuresets {
            let base_features: Vec<Feature> = featureset.iter().map(|x| x.clone()).collect();

            let name: String = featureset
                .iter()
                .map(|x| &x.name)
                .cloned()
                .collect_vec()
                .join("_");

            let name = format!("{}_{}", primitive.name, name);

            let new_feature =
                Feature::new(name, None, Some(primitive.clone()), Some(base_features));

            new_features.push(new_feature);
        }
    }

    return new_features;
}

#[cfg(test)]
mod tests {

    use std::collections::HashSet;

    use crate::{column_schema, create_feature, feature::Feature, input_set, primitive};

    use super::generate_features_for_primitive;

    #[test]
    fn test1() {
        let inputs = vec![
            input_set![["any", "numeric"], ["any", "numeric"]],
            input_set![["datetime", "any"], ["datetime", "any"]],
            input_set![["ordinal", "any"], ["ordinal", "any"]],
        ];

        let r_type = column_schema!["integer", "numeric"];

        let p = primitive!("GreaterThan", inputs, r_type, false);

        let f1 = create_feature!("f1", "double", "numeric");
        let f2 = create_feature!("f2", "integer", "numeric");
        let f3 = create_feature!("f3", "datetime", "");
        let f4 = create_feature!("f4", "datetime", "");
        let f5 = create_feature!("f5", "ordinal", "");
        let f6 = create_feature!("f6", "ordinal", "");

        let features = vec![
            f1.clone(),
            f2.clone(),
            f3.clone(),
            f4.clone(),
            f5.clone(),
            f6.clone(),
        ];
        let actual = generate_features_for_primitive(&p, &features);

        println!(
            "{:?}",
            actual
                .iter()
                .map(|x| x.name.clone())
                .collect::<Vec<String>>()
        );

        let expected = vec![
            create_feature!("fa", p.clone(), [f1.clone(), f2.clone()]),
            create_feature!("fb", p.clone(), [f2.clone(), f1.clone()]),
            create_feature!("fc", p.clone(), [f3.clone(), f4.clone()]),
            create_feature!("fd", p.clone(), [f4.clone(), f3.clone()]),
            create_feature!("fe", p.clone(), [f5.clone(), f6.clone()]),
            create_feature!("ff", p.clone(), [f6.clone(), f5.clone()]),
        ];

        let s1: HashSet<Feature> = HashSet::from_iter(actual.iter().cloned());
        let s2: HashSet<Feature> = HashSet::from_iter(expected.iter().cloned());

        assert_eq!(s1, s2);
    }
}
