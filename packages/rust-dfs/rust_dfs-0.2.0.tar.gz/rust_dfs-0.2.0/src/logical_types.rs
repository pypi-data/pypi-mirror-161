use serde::{Deserialize, Serialize};
use strum_macros::EnumIter;

#[derive(Debug, PartialEq, Eq, Hash, EnumIter, Copy, Clone, Serialize, Deserialize)]
pub enum LogicalTypes {
    Boolean,
    BooleanNullable,
    Address,
    Age,
    AgeFractional,
    Categorical,
    Datetime,
    Double,
    Integer,
    IntegerNullable,
    PostalCode,
    Ordinal,
    EmailAddress,
    LatLong,
    URL,
    NaturalLanguage,
    Timedelta,

    // Semantic Tags
    Numeric,
    TimeIndex,
    ForeignKey,
    DateOfBirth,
    Index,

    //Other - Hack?
    Any,
    Unknown,
}

impl TryFrom<&str> for LogicalTypes {
    type Error = ();

    fn try_from(v: &str) -> Result<Self, Self::Error> {
        let v = &v.to_lowercase()[..];

        match v {
            "boolean" => Ok(LogicalTypes::Boolean),
            "booleannullable" => Ok(LogicalTypes::BooleanNullable),
            "address" => Ok(LogicalTypes::Address),
            "age" => Ok(LogicalTypes::Age),
            "agefractional" => Ok(LogicalTypes::AgeFractional),
            "categorical" => Ok(LogicalTypes::Categorical),
            "datetime" => Ok(LogicalTypes::Datetime),
            "double" => Ok(LogicalTypes::Double),
            "integer" => Ok(LogicalTypes::Integer),
            "integernullable" => Ok(LogicalTypes::IntegerNullable),
            "postalcode" => Ok(LogicalTypes::PostalCode),
            "unknown" => Ok(LogicalTypes::Unknown),
            "ordinal" => Ok(LogicalTypes::Ordinal),
            "emailaddress" => Ok(LogicalTypes::EmailAddress),
            "latlong" => Ok(LogicalTypes::LatLong),
            "url" => Ok(LogicalTypes::URL),
            "naturallanguage" => Ok(LogicalTypes::NaturalLanguage),
            "timedelta" => Ok(LogicalTypes::Timedelta),

            // Semantic Tags
            "numeric" => Ok(LogicalTypes::Numeric),
            "timeindex" => Ok(LogicalTypes::TimeIndex),
            "foreignkey" => Ok(LogicalTypes::ForeignKey),
            "dateofbirth" => Ok(LogicalTypes::DateOfBirth),
            "index" => Ok(LogicalTypes::Index),

            //Other - Hack
            "any" => Ok(LogicalTypes::Any),
            _ => Err(()),
        }
    }
}
