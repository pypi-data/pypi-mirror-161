#![allow(dead_code)]
// use itertools::Itertools;
// use rust_dfs::column::Column;
// use rust_dfs::database_schema::DatabaseSchema;
// use rust_dfs::dfs::generate_features_for_primitive;
// use rust_dfs::feature::{generate_fake_features, Feature};
// use rust_dfs::logical_types::LogicalTypes;
// use rust_dfs::primitive::Primitive;
// use rust_dfs::table_schema::TableSchema;
// use rust_dfs::utils::print_bar;

// use rayon::prelude::*;
// use rust_dfs::feature::generate_fake_features;
// use std::fs::File;
// use std::io::prelude::*;
// use pyo3::prelude::*;

use rust_dfs::create_feature;

use rust_dfs::column_schema;
use rust_dfs::feature::Feature;
use rust_dfs::logical_types;

fn main() {
    println!("Hello World!"); // print_bar("FEATURETOOLS IN RUST");

    let f = create_feature!("dave", "integer", "numeric");

    println!("{}", f)
    // generate_fake_features(10);
    // logical_types_test();
    // features_test();
    // features_to_hashmap_test();
    // columns_test()
    // schema_test()
    // database_schema_test();
    // dfs_test()
    // primitives_test();
    // permutation_test();
    // test_generate_features();
}

// fn logical_types_test() {
//     print_bar("LOGICAL TYPES TEST");
// println!("{:?}", LogicalTypes::Boolean);
// println!("{:?}", LogicalTypes::BooleanNullable);

// let p1 = Primitive::new(LogicalTypes::BooleanNullable, "ABSOLUTE".to_string());
// println!("{}", p1);

// let mut vec = Vec::new();

// vec.push(LogicalTypes::Boolean);
// vec.push(LogicalTypes::BooleanNullable);
// vec.push(LogicalTypes::Boolean);

// vec.extend(vec![LogicalTypes::Boolean, LogicalTypes::Boolean]);

// println!("{:?}", vec);

// let lts1 = LogicalTypeSet::new(vec![LogicalTypes::Boolean, LogicalTypes::Boolean]);

// println!("{:?}", lts1);

// let lts2 = LogicalTypeSet::new(vec![
//     LogicalTypes::BooleanNullable,
//     LogicalTypes::BooleanNullable,
// ]);
// let lto1 = LogicalTypeOption::new(vec![lts1, lts2]);
// println!("{:?}", lto1);

// let j = serde_json::to_string(&LogicalTypes::Boolean);

// match j {
//     Ok(s) => println!("{}", s),
//     Err(e) => println!("{}", e),
// }
// Print, write to a file, or send to an HTTP server.
// println!("{}", j);
// }

// fn features_test() {
//     print_bar("FEATURES TEST");

//     let f1 = Feature::new(
//         "F1".to_string(),
//         LogicalTypes::Boolean,
//         LogicalTypes::Categorical,
//         None,
//     );
//     let f2 = Feature::new(
//         "F2".to_string(),
//         LogicalTypes::BooleanNullable,
//         LogicalTypes::Categorical,
//         None,
//     );

//     println!("{:?}", f1);
//     println!("{:?}", f2);

//     println!("{:?}", f2.logical_type);
//     println!("{}", f2);

//     let j = serde_json::to_string(&f1);

//     println!("--- FEATURE AS JSON");
//     match j {
//         Ok(s) => {
//             println!("{}", s);
//             let mut file = File::create("foo.txt").unwrap();
//             let p = format!("{}\n", s);
//             file.write_all(p.as_bytes()).expect("Error writing to file");
//         }
//         Err(e) => println!("{}", e),
//     }

//     f1.write_to_file();

//     let f4 = Feature::read_from_file("F2.json".to_string());

//     println!("Loaded feature from JSON: {:?}", f4);

//     // Ok(())
// }

// fn features_to_hashmap_test() {
//     print_bar("FEATURES TO HASHMAP TEST");

//     let f1 = Feature::new(
//         "F1".to_string(),
//         LogicalTypes::Boolean,
//         LogicalTypes::Categorical,
//         None,
//     );
//     let f2 = Feature::new(
//         "F2".to_string(),
//         LogicalTypes::BooleanNullable,
//         LogicalTypes::Categorical,
//         None,
//     );
//     let f3 = Feature::new(
//         "F3".to_string(),
//         LogicalTypes::BooleanNullable,
//         LogicalTypes::Categorical,
//         None,
//     );

//     let all_features = vec![&f1, &f2, &f3];

//     // let features_by_type = get_features_by_type(all_features);

//     // for logical_type in LogicalTypes::iter() {
//     //     println!("Searching for: {:?}", logical_type);
//     //     match features_by_type.get(&logical_type) {
//     //         Some(feature) => println!("Found Features: {:?}", feature),
//     //         None => println!("No feature found"),
//     //     }
//     // }
// }

// fn schema_test() {
//     print_bar("SCHEMA TEST");

//     TableSchema::read_from_file("schema_test_01.json".to_string());
// }

// fn database_schema_test() {
//     print_bar("DATABASE SCHEMA TEST");

//     DatabaseSchema::read_from_file("schema_final.json".to_string());
// }

// fn primitives_test() {
//     print_bar("PRIMITIVES TEST");

//     let primitives = Primitive::read_from_file("primitives.json".to_string());

//     println!("{:#?}", primitives);
// }

// fn permutation_test() {
//     use itertools::Itertools;

//     let a_features = vec![
//         "FA1".to_string(),
//         "FA2".to_string(),
//         "FA3".to_string(),
//         "FA4".to_string(),
//     ];
//     let b_features = vec!["F4".to_string(), "F5".to_string(), "F6".to_string()];
//     let c_features = vec!["F7".to_string(), "F8".to_string(), "F9".to_string()];

//     let perms = a_features.iter().permutations(2);

//     print_bar("PERMUTATIONS");
//     for p in perms {
//         println!("{:?}", p);
//     }

//     // P(A,A,B,B,C,C)
//     let combs1 = a_features.iter().combinations(2);
//     let combs2 = b_features.iter().combinations(2);
//     let combs3 = c_features.iter().combinations(2);

//     let a = (0..3).map(|i| (i * 2)..(i * 2 + 2));

//     for b in a {
//         println!("{:?}", b)
//     }

//     let c = vec![
//         vec!["F1".to_string(), "F2".to_string(), "F3".to_string()],
//         vec!["F4".to_string(), "F5".to_string(), "F6".to_string()],
//     ];

//     let d = c.iter().multi_cartesian_product();

//     for e in d {
//         println!("{:?}", e)
//     }

//     let dave1 = combs1.collect_vec();
//     let dave2 = combs2.collect_vec();
//     let dave3 = combs3.collect_vec();

//     println!("DAVE1 {:?}", dave1);

//     let dave11 = dave1.iter().map(|x| ("dave1", x)).collect_vec();
//     let dave22 = dave2.iter().map(|x| ("dave2", x)).collect_vec();
//     let dave33 = dave3.iter().map(|x| ("dave3", x)).collect_vec();

//     let dave4 = vec![dave11, dave22, dave33];
//     let f = dave4.iter().multi_cartesian_product();

//     for g in f {
//         // let s = g.into_iter().flatten().collect_vec();
//         println!("{:?}", g)
//     }

//     // println!("DAVE11 {:?}", dave11);
//     // let map = HashMap::from([("a", 1), ("b", 2), ("c", 3)]);

//     // vec![map.iter()].iter().multi_cartesian_product();

//     // println!("{:?}", map);
// }

// fn test_generate_features() {
//     let features = generate_fake_features(1000);

//     // println!("{:#?}", features);

//     let primitives = Primitive::read_from_file("data/primitives.json".to_string());

//     let t1_primitives: Vec<&Primitive> = primitives
//         .iter()
//         .filter(|x| x.function_type == "transform")
//         .collect();

//     // println!("{:#?}", t1_primitives);

//     let features_ref = &features;

//     // let mut total = 0;
//     // let mut prim_names = Vec::new();

//     // let p_equal_array: Vec<&Primitive> = t1_primitives
//     //     .iter()
//     //     .filter(|x| x.name == "Equal")
//     //     .cloned()
//     //     .collect();

//     // let p_equal = p_equal_array[0];

//     // let featuresets = generate_features_for_primitive(p_equal, features_ref);

//     // println!("{:#?}", featuresets);

//     // let mut new_features: Vec<Feature> = Vec::new();

//     let new_features: Vec<Feature> = t1_primitives
//         .par_iter()
//         // .iter()
//         .map(|&p| generate_features_for_primitive(p, features_ref))
//         .flatten()
//         .collect();

//     println!("TOTAL: {:#?}", new_features.len());

//     // for p in t1_primitives {
//     //     let mut features = generate_features_for_primitive(&p, features_ref);
//     //     total += features.len();

//     //     if features.len() > 0 {
//     //         let a = format!("{}", p.name);
//     //         good_prims.push(a);
//     //     }

//     //     new_features.append(&mut features);
//     // }

//     // println!("TOTAL: {}", total);

//     // println!("{:#?}", good_prims);
//     // println!("{:#?}", new_features);

//     // Feature::write_many_to_file(
//     //     &new_features,
//     //     "/Users/dreed/code/ft_benchmark/500_rust_features.json".to_string(),
//     // );
// }
