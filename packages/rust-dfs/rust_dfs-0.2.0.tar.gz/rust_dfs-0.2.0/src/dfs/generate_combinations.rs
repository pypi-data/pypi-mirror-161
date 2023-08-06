use crate::{column_schema::ColumnSchema, feature::Feature};
use itertools::Itertools;

pub fn generate_combinations(
    features: Vec<(ColumnSchema, Feature)>,
    n: usize,
    is_commutative: bool,
) -> Vec<Vec<(ColumnSchema, Feature)>> {
    if is_commutative {
        features.iter().cloned().combinations(n).collect_vec()
    } else {
        features.iter().cloned().permutations(n).collect_vec()
    }
}

#[cfg(test)]
mod tests {
    use super::generate_combinations;
    use crate::{column_schema, create_feature};
    #[test]
    fn test_generate_combinations() {
        // let c = column_schema!("boolean", "none");
        // let fa_1 = create_feature!("FA_1", c.clone());
        // let fa_2 = create_feature!("FA_2", c.clone());
        // let fa_3 = create_feature!("FA_3", c.clone());

        // let features = vec![(c.clone(), &fa_1), (c.clone(), &fa_2), (c.clone(), &fa_3)];
        // let actual = generate_combinations(features, 2, true);

        // let expected = vec![
        //     vec![(c.clone(), &fa_1), (c.clone(), &fa_2)],
        //     vec![(c.clone(), &fa_1), (c.clone(), &fa_3)],
        //     vec![(c.clone(), &fa_2), (c.clone(), &fa_3)],
        // ];

        // assert_eq!(actual, expected);
    }
}
