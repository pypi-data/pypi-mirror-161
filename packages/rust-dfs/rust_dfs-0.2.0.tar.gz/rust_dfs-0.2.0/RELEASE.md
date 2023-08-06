## [Unreleased]

## [0.2.0] - 2022-07-30
### Other
- adding action to deploy docs
### Rust
- removed `input_set` in favor of `column_schema`(#5)
- created a hashmap that keys by both logical_type and semantic_tag and then finds set interception between them for matching features to a primitive (#5)
- primitive types that can't be found are tagged as "Any". So a Primitive that has an input of ["", "Numeric"], can match to a feature that has any logical_type and a semantic tag of Numeric. (#5)
- removed a lot of references in place of `.clone()`. This will need to be revisited. (#5)
- created directory for feature related code (#5)
### Python
- added `time_index` argument to `generate_fake_dataframe` to create a time index (#5)
- fixed tests to test all logical types (#5)

## [0.1.6] - 2022-07-21
### Python
- added convert primitive utility (#2)
- made gen_dataframe utility more generic (#2)
### Rust
- create `input_set!` macro (#2)
- moved input_set code out to its own file (#2)
- added equality checks to Feature struct (#2)
- added hashing to Feature  (#2)
- added comparison code (#2)

## [0.1.5] - 2022-07-19
### Rust
- Added `feature!` macro
- Added `primitive!` macro