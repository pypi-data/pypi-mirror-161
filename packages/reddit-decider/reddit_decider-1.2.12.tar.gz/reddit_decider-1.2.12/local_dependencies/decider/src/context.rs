use crate::{value_eq, BucketingField, Comp, DeciderError};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;

/// A context captures the relevant state in which we want to find out whether a feature
/// should be available.
#[derive(Deserialize, Debug, Clone, Default, PartialEq)]
pub struct Context {
    pub user_id: Option<String>,

    /// IETF language tag representing the preferred locale for the client, used for
    /// providing localized content. Consists of an ISO 639-1 primary language subtag and
    /// an optional ISO 3166-1 alpha-2 region subtag separated by an underscore.
    ///
    /// e.g. `en`, `en_US`.
    pub locale: Option<String>,

    /// A two-character ISO 3166-1 country code.
    ///
    /// e.g. `US`.
    pub country_code: Option<String>,
    pub device_id: Option<String>,
    pub canonical_url: Option<String>,
    pub origin_service: Option<String>,
    pub user_is_employee: Option<bool>,
    pub logged_in: Option<bool>,
    pub app_name: Option<String>,
    pub build_number: Option<i32>,
    pub auth_client_id: Option<String>,
    pub cookie_created_timestamp: Option<i64>,
    pub other_fields: Option<HashMap<String, Value>>,
}

impl Context {
    pub(super) fn for_bucketing_field(bv: BucketingField, bucketing_value: String) -> Context {
        Context::default().with_bucketing_field(bv, bucketing_value)
    }

    pub(super) fn with_bucketing_field(
        &self,
        bucketing_field: BucketingField,
        bucketing_value: String,
    ) -> Context {
        let mut out = self.clone();
        match bucketing_field {
            BucketingField::UserId => out.user_id = Some(bucketing_value),
            BucketingField::DeviceId => out.device_id = Some(bucketing_value),
            BucketingField::CanonicalUrl => out.canonical_url = Some(bucketing_value),
        }
        out
    }

    pub(super) fn get_bucketing_field(
        &self,
        bucketing_field: BucketingField,
    ) -> Result<String, DeciderError> {
        let field_value = match bucketing_field {
            BucketingField::UserId => self.user_id.clone(),
            BucketingField::DeviceId => self.device_id.clone(),
            BucketingField::CanonicalUrl => self.canonical_url.clone(),
        };

        field_value.ok_or(DeciderError::MissingBucketingFieldInContext(
            bucketing_field,
        ))
    }

    pub(super) fn cmp(&self, field: &ContextField, value: &Value) -> Option<bool> {
        field
            .get_value(self)
            .and_then(|other| value_eq(value, &other))
    }

    pub(super) fn cmp_op(&self, comp: Comp, field: &ContextField, rhs: f64) -> Option<bool> {
        // GT/LT and friends only really make sense on Numbers, but sometimes might
        // show up as Strings in the experiment_config.json
        self.field_to_float(field)
            .map(|lhs| comp.cmp_floats(lhs, rhs))
    }

    fn field_to_float(&self, field: &ContextField) -> Option<f64> {
        match field.get_value(self) {
            Some(Value::Number(n)) => n.as_f64(),
            Some(Value::String(s)) => s.parse::<f64>().ok(),
            _ => None,
        }
    }
}

/// `ContextField` provides a set of type-safe values for accessing fields inside a [`Context`].
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(from = "String", into = "String")]
pub(super) enum ContextField {
    UserId,
    DeviceId,
    CanonicalUrl,
    Locale,
    CountryCode,
    OriginService,
    AppName,
    UserIsEmployee,
    LoggedIn,
    BuildNumber,
    CookieCreatedTimestamp,
    AuthClientId,
    Other(String),
}

impl ContextField {
    pub(super) fn get_value(&self, ctx: &Context) -> Option<Value> {
        match self {
            Self::UserId => ctx.user_id.as_deref().map(Value::from),
            Self::DeviceId => ctx.device_id.as_deref().map(Value::from),
            Self::CanonicalUrl => ctx.canonical_url.as_deref().map(Value::from),
            Self::Locale => ctx.locale.as_deref().map(Value::from),
            Self::CountryCode => ctx.country_code.as_deref().map(Value::from),
            Self::OriginService => ctx.origin_service.as_deref().map(Value::from),
            Self::AppName => ctx.app_name.as_deref().map(Value::from),
            Self::UserIsEmployee => ctx.user_is_employee.map(Value::from),
            Self::LoggedIn => ctx.logged_in.map(Value::from),
            Self::BuildNumber => ctx.build_number.map(Value::from),
            Self::CookieCreatedTimestamp => ctx.cookie_created_timestamp.map(Value::from),
            Self::AuthClientId => ctx.auth_client_id.as_deref().map(Value::from),
            Self::Other(field) => ctx
                .other_fields
                .as_ref()
                .and_then(|hm| hm.get(field as &str).cloned()),
        }
    }
}

impl From<String> for ContextField {
    fn from(sval: String) -> Self {
        match sval.as_str() {
            "user_id" => Self::UserId,
            "device_id" => Self::DeviceId,
            "canonical_url" => Self::CanonicalUrl,
            "locale" => Self::Locale,
            "country_code" => Self::CountryCode,
            "origin_service" => Self::OriginService,
            "app_name" => Self::AppName,
            "user_is_employee" => Self::UserIsEmployee,
            "logged_in" => Self::LoggedIn,
            "build_number" => Self::BuildNumber,
            "cookie_created_timestamp" => Self::CookieCreatedTimestamp,
            "auth_client_id" => Self::AuthClientId,
            _ => Self::Other(sval),
        }
    }
}

impl AsRef<str> for ContextField {
    fn as_ref(&self) -> &str {
        match self {
            Self::UserId => "user_id",
            Self::DeviceId => "device_id",
            Self::CanonicalUrl => "canonical_url",
            Self::Locale => "locale",
            Self::CountryCode => "country_code",
            Self::OriginService => "origin_service",
            Self::AppName => "app_name",
            Self::UserIsEmployee => "user_is_employee",
            Self::LoggedIn => "logged_in",
            Self::BuildNumber => "build_number",
            Self::CookieCreatedTimestamp => "cookie_created_timestamp",
            Self::AuthClientId => "auth_client_id",
            Self::Other(field) => field.as_str(),
        }
    }
}

impl From<ContextField> for String {
    fn from(field: ContextField) -> Self {
        field.as_ref().to_string()
    }
}

#[cfg(test)]
mod tests {
    mod context {
        use super::super::Context;
        use crate::generators::{bucketing_field, context_strategy};
        use crate::{BucketingField, DeciderError};
        use proptest::option;
        use proptest::prelude::*;

        proptest! {
            #[test]
            fn test_for_bucketing_field(
                bucketing_field in bucketing_field(),
                bucketing_value in ".*",
            ) {
                let bv = bucketing_value.clone();
                let expected_ctx = match bucketing_field {
                    BucketingField::UserId => Context {
                        user_id: Some(bv),
                        ..Context::default()
                    },
                    BucketingField::DeviceId => Context {
                        device_id: Some(bv),
                        ..Context::default()
                    },
                    BucketingField::CanonicalUrl => Context {
                        canonical_url: Some(bv),
                        ..Context::default()
                    },
                };

                prop_assert_eq!(expected_ctx, Context::for_bucketing_field(bucketing_field, bucketing_value));
            }

            #[test]
            fn test_with_bucketing_field(
                ctx in context_strategy(),
                bucketing_field in bucketing_field(),
                bucketing_value in ".*",
            ) {
                let bv = bucketing_value.clone();
                let expected_ctx = match bucketing_field {
                    BucketingField::UserId => Context {
                        user_id: Some(bv),
                        ..ctx.clone()
                    },
                    BucketingField::DeviceId => Context {
                        device_id: Some(bv),
                        ..ctx.clone()
                    },
                    BucketingField::CanonicalUrl => Context {
                        canonical_url: Some(bv),
                        ..ctx.clone()
                    }
                };

                prop_assert_eq!(expected_ctx, ctx.with_bucketing_field(bucketing_field, bucketing_value));
            }

            #[test]
            fn test_get_bucketing_field(
                mut ctx in context_strategy(),
                bucketing_field in bucketing_field(),
                bucketing_value_opt in option::of(".*"),
            ) {
                let bvo = bucketing_value_opt.clone();
                match bucketing_field {
                    BucketingField::UserId => ctx.user_id = bvo,
                    BucketingField::DeviceId => ctx.device_id = bvo,
                    BucketingField::CanonicalUrl => ctx.canonical_url = bvo,
                }

                let result = ctx.get_bucketing_field(bucketing_field);

                match bucketing_value_opt {
                    Some(bucketing_value) => prop_assert_eq!(result.unwrap(), bucketing_value),
                    None => {
                        match result.unwrap_err() {
                            DeciderError::MissingBucketingFieldInContext(actual_field) => prop_assert_eq!(bucketing_field, actual_field),
                            _ => prop_assert!(false, "bucketing fields don't match"),
                        }
                    },
                };
            }
        }
    }

    pub(super) mod context_field {
        use super::super::ContextField;
        use proptest::prelude::*;
        use serde_json::Value;

        proptest! {
            #[test]
            fn test_from_string((field, tag) in context_field_strategy()) {
                let other = ContextField::from(tag);
                prop_assert_eq!(field, other);
            }

            #[test]
            fn test_serialize((field, tag) in context_field_strategy()) {
                let serialized = serde_json::to_value(&field).unwrap();
                prop_assert_eq!(Value::from(tag), serialized);
            }

            #[test]
            fn test_deserialize((field, tag) in context_field_strategy()) {
                let json_str = format!(r#""{}""#, tag);
                let deserialized: ContextField = serde_json::from_str(&json_str).unwrap();
                prop_assert_eq!(field, deserialized);
            }
        }

        pub(super) fn context_field_strategy() -> impl Strategy<Value = (ContextField, String)> {
            let other_strategy = "\\w+".prop_filter_map("got string with specific field", |s| {
                match ContextField::from(s.clone()) {
                    cf @ ContextField::Other(_) => Some((cf, s)),
                    _ => None,
                }
            });

            prop_oneof![
                Just((ContextField::UserId, "user_id".to_string())),
                Just((ContextField::DeviceId, "device_id".to_string())),
                Just((ContextField::CanonicalUrl, "canonical_url".to_string())),
                Just((ContextField::Locale, "locale".to_string())),
                Just((ContextField::CountryCode, "country_code".to_string())),
                Just((ContextField::OriginService, "origin_service".to_string())),
                Just((ContextField::AppName, "app_name".to_string())),
                Just((ContextField::UserIsEmployee, "user_is_employee".to_string())),
                Just((ContextField::LoggedIn, "logged_in".to_string())),
                Just((ContextField::BuildNumber, "build_number".to_string())),
                Just((
                    ContextField::CookieCreatedTimestamp,
                    "cookie_created_timestamp".to_string()
                )),
                Just((ContextField::AuthClientId, "auth_client_id".to_string())),
                other_strategy
            ]
        }
    }
}
