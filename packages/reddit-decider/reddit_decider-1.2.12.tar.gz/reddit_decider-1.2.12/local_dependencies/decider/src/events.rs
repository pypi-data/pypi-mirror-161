use chrono::Utc;
use std::error::Error;
use std::fmt::{Debug, Display, Formatter};
use std::num::TryFromIntError;

use crate::Event as DecisionEvent;
use crate::{BucketingField, Context, DecisionKind};
use serde::ser::SerializeMap;
use serde::{Serialize, Serializer};
use uuid::Uuid;

// Consts for the experiment SAN.
const SOURCE: Thrifty<&'static str> = Thrifty {
    value: "experiment",
};

const ACTION: Thrifty<&'static str> = Thrifty { value: "expose" };

const NOUN_USER_ID: Thrifty<&'static str> = Thrifty { value: "user_id" };
const NOUN_DEVICE_ID: Thrifty<&'static str> = Thrifty { value: "device_id" };
const NOUN_CANONICAL_URL: Thrifty<&'static str> = Thrifty {
    value: "canonical_url",
};

/// `EventStrings` holds serialized strings representing exposure events.
///
/// `event_data` use the legacy format: values are separated by "::::" and are parsed by the python
/// client.
///
/// `event_json` represents a fully hydrated thrift event that can be sent to the V2 events
/// collector.  
pub(crate) struct SerializedEvents {
    pub(crate) event_data: Vec<String>,
    pub(crate) events: Vec<DecisionEvent>,
}

impl SerializedEvents {
    pub(crate) fn new(
        ctx: &Context,
        internal_events: Vec<ExperimentEvent>,
    ) -> Result<Self, Box<dyn Error>> {
        let client_timestamp = &Utc::now().timestamp_millis().into();

        // All events for a single decision share the same correlation id.
        let correlation_id = &Uuid::new_v4().into();

        let app = &App::new(ctx).map(Thrifty::from);
        let platform = &Platform::new(ctx).map(Thrifty::from);
        let request = &Request::new(ctx).map(Thrifty::from);
        let user = &User::new(ctx).map(Thrifty::from);
        let geo = &Geo::new(ctx).map(Thrifty::from);

        let num_events = internal_events.len();

        internal_events
            .into_iter()
            // For each event...
            .map(|exp_ev| {
                // First, hydrate the legacy format string.
                let data_string = exp_ev.to_string();

                let noun = match &exp_ev.bucketing_field {
                    BucketingField::UserId => NOUN_USER_ID,
                    BucketingField::DeviceId => NOUN_DEVICE_ID,
                    BucketingField::CanonicalUrl => NOUN_CANONICAL_URL,
                };

                let kind = exp_ev.decision_kind;

                // Then, try to create an experiment from the available pieces.
                Experiment::try_from(exp_ev)
                    .map(|exp| {
                        let event = Event {
                            source: SOURCE,
                            action: ACTION,
                            noun,
                            client_timestamp,
                            uuid: Uuid::new_v4().into(),
                            correlation_id,
                            app,
                            platform,
                            request,
                            user,
                            experiment: exp.into(),
                            geo,
                        };
                        (data_string, kind, event)
                    })
                    // Box any errors to unify with the serde errors in the fold.
                    .map_err(|err| err.into())
            })
            // Roll the results up into the holder struct. `try_fold` will return early if it
            // encounters an error.
            .try_fold::<_, _, Result<SerializedEvents, Box<dyn Error>>>(
                SerializedEvents {
                    event_data: Vec::with_capacity(num_events),
                    events: Vec::with_capacity(num_events),
                },
                |mut acc, event_res: Result<(String, DecisionKind, Event<'_>), Box<dyn Error>>| {
                    let (data_string, kind, event) = event_res?;
                    acc.event_data.push(data_string);

                    let json_string = serde_json::to_string(&event)
                        .map_err::<Box<dyn Error>, _>(|err| err.into())?;

                    let decision_event = DecisionEvent {
                        kind,
                        json: json_string,
                    };

                    acc.events.push(decision_event);

                    Ok(acc)
                },
            )
    }
}

/// `Event` is a serde proxy for the V2 event struct. Note that in order to avoid a dependency on
/// thrift, this struct is its own minimal version of the TJsonProtocol.
///
/// The thrift JSON protocol uses the field indices as json map keys, and encodes all types as
/// objects:
/// - Strings are encoded as `{"str": $value}`.
/// - Integers are encoded as `{"i32": $value}`, or `{"i64": $value}`.
/// - Booleans are encoded as `{"tf": $value}`, where $value is `1` when true and `0` when false.
/// - Substructs are encoded as `{"rec": { ... }}`, with each struct field encoded using these same
///   rules.
///
/// There are other thrift types with their own encoding, but this is irrelevant for encoding the
/// event struct. Since thrift indices cannot change without breaking clients this encoding is safe
/// to use until the V2 events collector starts using a different protocol altogether.
///
/// Encoding these values is done by wrapping them in [Thrifty] and implementing [Tagged]. Refer to
/// those types to see how they work. For information on the thrift schema for V2 events, see
/// [here](https://github.snooguts.net/reddit/data-schemas/blob/master/schemas/event.thrift#L136).
#[derive(Debug, Serialize)]
struct Event<'ev> {
    // Source is always "experiment".
    #[serde(rename = "1")]
    source: Thrifty<&'static str>,

    // Action is always "expose".
    #[serde(rename = "2")]
    action: Thrifty<&'static str>,

    // Noun is one of: "user_id", "device_id", or "canonical_url", depending on the bucketing field
    // of the returned event.
    #[serde(rename = "3")]
    noun: Thrifty<&'static str>,

    // An arbitrary timestamp of when these events are generated.
    #[serde(rename = "5")]
    client_timestamp: &'ev Thrifty<i64>,

    // A random Uuid.
    #[serde(rename = "6")]
    uuid: Thrifty<Uuid>,

    // A Uuid that links multiple related events. This implementation sets the same Uuid on all
    // events generated from a single Decision.
    #[serde(rename = "8")]
    correlation_id: &'ev Thrifty<Uuid>,

    #[serde(rename = "107", skip_serializing_if = "Option::is_none")]
    app: &'ev Option<Thrifty<App<'ev>>>,

    #[serde(rename = "108", skip_serializing_if = "Option::is_none")]
    platform: &'ev Option<Thrifty<Platform>>,

    #[serde(rename = "109", skip_serializing_if = "Option::is_none")]
    request: &'ev Option<Thrifty<Request<'ev>>>,

    #[serde(rename = "112", skip_serializing_if = "Option::is_none")]
    user: &'ev Option<Thrifty<User<'ev>>>,

    #[serde(rename = "129")]
    experiment: Thrifty<Experiment>,

    #[serde(rename = "500", skip_serializing_if = "Option::is_none")]
    geo: &'ev Option<Thrifty<Geo<'ev>>>,
}

/// The `App` substruct of the V2 event. The schema is available
/// [here](https://github.snooguts.net/reddit/data-schemas/blob/master/schemas/components/device.thrift#L177:8).
#[derive(Clone, Debug, Serialize)]
struct App<'a> {
    // The name of the app/code base sending the event.
    //
    // Expected values:
    //     * web: desktop site
    //     * web2x: redesigned desktop site
    //     * mweb: mobile site
    //     * ios: Reddit-native iOS app
    //     * android: Reddit-native Android app
    //     * amp: Google's Accelerated Mobile Pages
    //     * mweb3x: lightweight, blazing fast, mobile-first frontend service
    //     * third party app name lowercased with _ for spaces
    //
    // Event-collector will reject an event if name does not satisfy this regex: ^[-_a-z0-9]+$
    //
    // Extracted from `Context.app_name`. This field is required by the event collector. If it's not
    // set, the entire substruct is elided.
    #[serde(rename = "2")]
    name: Thrifty<&'a str>,

    // Extracted from `Context.build_number`.
    #[serde(rename = "4", skip_serializing_if = "Option::is_none")]
    build_number: Option<Thrifty<i32>>,

    // Extracted from `Context.locale`.
    #[serde(rename = "6", skip_serializing_if = "Option::is_none")]
    relevant_locale: Option<Thrifty<&'a str>>,
}

impl App<'_> {
    fn new(ctx: &Context) -> Option<App<'_>> {
        ctx.app_name.as_ref().map(|name| App {
            name: name.as_str().into(),
            build_number: ctx.build_number.map(Thrifty::from),
            relevant_locale: ctx.locale.as_ref().map(|locale| locale.as_str().into()),
        })
    }
}

/// The `Platform` substruct of the V2 event. The schema is available
/// [here](https://github.snooguts.net/reddit/data-schemas/blob/master/schemas/components/device.thrift#L93:8).
#[derive(Clone, Debug, Serialize)]
struct Platform {
    // Extracted from `Context.device_id`. Since this is the only field we set on the substruct, the
    // entire substruct is elided if it's not set on the context.
    #[serde(rename = "2")]
    device_id: Thrifty<Uuid>,
}

impl Platform {
    fn new(ctx: &Context) -> Option<Self> {
        ctx.device_id.as_ref().and_then(|uuid_str| {
            let uuid = Uuid::try_parse(uuid_str).ok()?;

            Some(Platform {
                device_id: uuid.into(),
            })
        })
    }
}

/// The `Request` substruct of the V2 event. The schema is available
/// [here](https://github.snooguts.net/reddit/data-schemas/blob/master/schemas/components/request.thrift#L9).
#[derive(Clone, Debug, Serialize)]
struct Request<'a> {
    // Extracted from `Context.canonical_url`. Since this is the only field we set on the substruct,
    // the entire substruct is elided if it's not set on the context.
    #[serde(rename = "17")]
    canonical_url: Thrifty<&'a str>,
}

impl Request<'_> {
    fn new(ctx: &Context) -> Option<Request<'_>> {
        ctx.canonical_url.as_ref().map(|curl_str| Request {
            canonical_url: curl_str.as_str().into(),
        })
    }
}

/// The `User` substruct of the V2 event. The schema is available
/// [here](https://github.snooguts.net/reddit/data-schemas/blob/master/schemas/components/user.thrift#L9:8).
#[derive(Clone, Debug, Serialize)]
struct User<'a> {
    // Extracted from `Context.user_id`. This field is required by the event collector. If it's not
    // set, the entire substruct is elided.
    #[serde(rename = "1")]
    user_id: Thrifty<&'a str>,

    // Extracted from `Context.logged_in`.
    #[serde(rename = "3", skip_serializing_if = "Option::is_none")]
    logged_in: Option<Thrifty<bool>>,

    // Extracted from `Context.cookie_created_timestamp`.
    #[serde(rename = "4", skip_serializing_if = "Option::is_none")]
    cookie_created_timestamp: Option<Thrifty<i64>>,

    // Extracted from `Context.user_is_employee`.
    #[serde(rename = "16", skip_serializing_if = "Option::is_none")]
    is_employee: Option<Thrifty<bool>>,
}

impl User<'_> {
    fn new(ctx: &Context) -> Option<User<'_>> {
        ctx.user_id.as_ref().map(|user_id| User {
            user_id: user_id.as_str().into(),
            logged_in: ctx.logged_in.map(Thrifty::from),
            cookie_created_timestamp: ctx.cookie_created_timestamp.map(Thrifty::from),
            is_employee: ctx.user_is_employee.map(Thrifty::from),
        })
    }
}

/// The `Experiment` substruct of the V2 event. Unlike the other substructs, the data here are
/// extracted from the event returned in the decision, not from the context. Therefore both the
/// struct and its fields are required; we know they must be available or we wouldn't be hydrating
/// the event.
///
/// The schema is available [here](https://github.snooguts.net/reddit/data-schemas/blob/master/schemas/components/experiment.thrift#L9).
#[derive(Clone, Debug, Serialize)]
struct Experiment {
    // Extracted from `Event.feature_id`.
    #[serde(rename = "1")]
    experiment_id: Thrifty<i64>,

    // Extracted from `Event.feature_name`.
    #[serde(rename = "2")]
    name: Thrifty<String>,

    // Extracted from `Event.experiment_owner`.
    #[serde(rename = "3")]
    owner: Thrifty<String>,

    // Extracted from `Event.variant_name`.
    #[serde(rename = "4")]
    variant: Thrifty<String>,

    // Extracted from `Event.start_ts`. The timestamp is in milliseconds UTC.
    #[serde(rename = "5")]
    start_ts: Thrifty<i64>,

    // Extracted from `Event.stop_ts`. The timestamp is in milliseconds UTC.
    #[serde(rename = "6")]
    stop_ts: Thrifty<i64>,

    // Extracted from `Event.bucketing_field`.
    #[serde(rename = "7")]
    bucketing_key: Thrifty<String>,

    // Extracted from `Event.feature_version`.
    #[serde(rename = "8")]
    version: Thrifty<String>,

    // Extracted from `Event.bucketing_value`.
    #[serde(rename = "9")]
    bucketing_value: Thrifty<String>,

    // `true` when the decision kind is `OVERRIDE`, otherwise `false`.
    #[serde(rename = "10")]
    is_override: Thrifty<bool>,
}

impl TryFrom<ExperimentEvent> for Experiment {
    type Error = TryFromIntError;

    fn try_from(value: ExperimentEvent) -> Result<Self, Self::Error> {
        let experiment_id = i64::from(value.feature_id).into();
        let name = value.feature_name.into();
        let owner = value.owner.into();
        let variant = value.variant_name.into();
        let start_ts = i64::try_from(value.start_ts)?.into();
        let stop_ts = i64::try_from(value.stop_ts)?.into();
        let bucketing_key = value.bucketing_field.to_string().into();
        let version = value.feature_version.to_string().into();
        let bucketing_value = value.bucketing_value.into();
        let is_override = (value.decision_kind == DecisionKind::Override).into();

        Ok(Experiment {
            experiment_id,
            name,
            owner,
            variant,
            start_ts,
            stop_ts,
            bucketing_key,
            version,
            bucketing_value,
            is_override,
        })
    }
}

/// The `Geo` substruct of the V2 event. The schema is available
/// [here](https://github.snooguts.net/reddit/data-schemas/blob/master/schemas/components/midas.thrift#L19).
#[derive(Clone, Debug, Serialize)]
struct Geo<'a> {
    // Extracted from `Context.country_code`. Since this is the only field we set on the substruct,
    // the entire substruct is elided if it's not set on the context.
    #[serde(rename = "1")]
    country_code: Thrifty<&'a str>,
}

impl Geo<'_> {
    fn new(ctx: &Context) -> Option<Geo<'_>> {
        ctx.country_code.as_ref().map(|cc_str| Geo {
            country_code: cc_str.as_str().into(),
        })
    }
}

/// `ExperimentEvent` is an internal type that holds event information from a decision. These events
/// are used to hydrate the [EventStrings] struct when the decision is returned to the caller.
#[derive(Clone, Debug)]
pub(crate) struct ExperimentEvent {
    pub(crate) decision_kind: DecisionKind,
    pub(crate) feature_id: u32,
    pub(crate) feature_name: String,
    pub(crate) feature_version: u32,
    pub(crate) variant_name: String,
    pub(crate) bucketing_field: BucketingField,
    pub(crate) bucketing_value: String,
    pub(crate) start_ts: u64,
    pub(crate) stop_ts: u64,
    pub(crate) owner: String,
}

// TODO Remove this trait once we've migrated off the legacy string format.
impl Display for ExperimentEvent {
    /// Formats the event into the legacy string format.
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{}::::{}::::{}::::{}::::{}::::{}::::{}::::{}::::{}::::{}",
            self.decision_kind as u8,
            self.feature_id,
            self.feature_name,
            self.feature_version,
            self.variant_name,
            self.bucketing_value,
            self.bucketing_field,
            self.start_ts,
            self.stop_ts,
            self.owner,
        )
    }
}

/// `Tagged` associates a type with a thrift field tag; for example, `"str"` for strings, or values
/// that are encoded as strings. The [impl_tagged] macro is available in this module to make
/// implementing this trait less annoying.
trait Tagged {
    const TAG: &'static str;
}

macro_rules! impl_tagged {
    ($tag:expr, [$($typ:ty),+]) => {
        $(
            impl Tagged for $typ {
                const TAG: &'static str = $tag;
            }
        )+
    };

    ($tag:expr, $typ:ty) => {
        impl_tagged!($tag, [$typ]);
    };
}

impl_tagged!("str", [&str, String, Uuid]);
impl_tagged!("i32", i32);
impl_tagged!("i64", i64);
impl_tagged!("rec", [App<'_>, Experiment, Geo<'_>, Platform, Request<'_>, User<'_>]);

/// `Thrifty` is a wrapper that ensures values are encoded using the thrift json protocol. When `T`
/// is `Serializable + Tagged`, `Thrifty<T>` is encoded as `{$tag: $value}`.
///
/// Note that thrift bools are encoded as integers with a custom tag, and so have a wholly unique
/// `Serialize` implementation.
struct Thrifty<T> {
    value: T,
}

impl Serialize for Thrifty<bool> {
    fn serialize<S: Serializer>(&self, serializer: S) -> Result<S::Ok, S::Error> {
        let ival = if self.value { 1 } else { 0 };

        let mut map = serializer.serialize_map(Some(1))?;
        map.serialize_entry("tf", &ival)?;
        map.end()
    }
}

impl<T> Serialize for Thrifty<T>
where
    T: Serialize + Tagged,
{
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut map = serializer.serialize_map(Some(1))?;
        map.serialize_entry(<T as Tagged>::TAG, &self.value)?;
        map.end()
    }
}

impl<T> From<T> for Thrifty<T> {
    fn from(value: T) -> Self {
        Thrifty { value }
    }
}

impl<T: Clone> Clone for Thrifty<T> {
    fn clone(&self) -> Self {
        Thrifty {
            value: self.value.clone(),
        }
    }
}

impl<T: Debug> Debug for Thrifty<T> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "Thrifty {{ value: {:?} }}", self.value)
    }
}

#[cfg(test)]
mod tests {
    use crate::{DecisionKind, ExperimentEvent};
    use proptest::prelude::*;

    pub(super) mod app {
        use super::super::*;
        use crate::generators::context_strategy;
        use prop::option;
        use proptest::prelude::*;
        use serde_json::{json, Value};

        proptest! {
            #[test]
            fn test_new(ctx in context_strategy()) {
                let app = App::new(&ctx);
                if ctx.app_name.is_none() {
                    prop_assert!(app.is_none());
                } else {
                    prop_assert!(app.is_some());

                    let app = app.unwrap();
                    prop_assert_eq!(ctx.app_name.as_ref().unwrap(), &app.name.value);
                    prop_assert_eq!(ctx.build_number, app.build_number.map(|t| t.value));

                    let rl = app.relevant_locale.map(|t| t.value.to_owned());
                    prop_assert_eq!(ctx.locale.as_ref(), rl.as_ref());
                }
            }

            #[test]
            fn test_serialize((app, expected_value) in app_strategy()) {
                let serialized = serde_json::to_value(app.clone()).unwrap();

                prop_assert_eq!(expected_value, serialized);
            }
        }

        prop_compose! {
            pub(super) fn app_strategy()(
                app_name in ".*",
                build_number in option::of(prop::num::i32::ANY),
                relevant_locale in option::of(".*"),
            ) -> (App<'static>, Value) {
                // N.B. Leak is ok since this is only for the unit test, value doesn't live long.
                // This is used to simplify lifetime management in tests without resorting to owned
                // types.
                let name_str: &'static str = Box::leak(app_name.clone().into_boxed_str());
                let relevant_locale_arg: Option<Thrifty<&'static str>> = relevant_locale.clone().map(|os| {
                    let locale_str: &'static str = Box::leak(os.into_boxed_str());
                    locale_str.into()
                });

                let app = App {
                    name: name_str.into(),
                    build_number: build_number.map(Thrifty::from),
                    relevant_locale: relevant_locale_arg,
                };


                let mut expected_value = json!({
                    "2": {
                        "str": app_name,
                    },
                });

                if let Some(bnv) = build_number {
                    expected_value.as_object_mut().unwrap().insert("4".to_string(), json!({
                        "i32": bnv
                    }));
                }
                if let Some(rlv) = relevant_locale {
                    expected_value.as_object_mut().unwrap().insert("6".to_string(), json!({
                        "str": rlv,
                    }));
                }

                (app, expected_value)
            }
        }
    }

    pub(super) mod platform {
        use super::super::*;
        use super::*;
        use crate::generators::*;
        use serde_json::{json, Value};

        proptest! {
            #[test]
            fn test_new_bad_uuid(mut ctx in context_strategy(), uuid in ".*") {
                ctx.device_id = Some(uuid);

                let platform = Platform::new(&ctx);
                prop_assert!(platform.is_none());
            }

            #[test]
            fn test_new(ctx in context_strategy()) {
                let platform = Platform::new(&ctx);

                if ctx.device_id.is_none() {
                    prop_assert!(platform.is_none());
                } else {
                    prop_assert!(platform.is_some());

                    let platform = platform.unwrap();
                    let expected_device_id = Uuid::try_parse(&ctx.device_id.unwrap()).unwrap();
                    prop_assert_eq!(expected_device_id, platform.device_id.value);
                }
            }

            #[test]
            fn test_serialize((platform, expected_value) in platform_strategy()) {
                let serialized = serde_json::to_value(platform).unwrap();
                prop_assert_eq!(expected_value, serialized);
            }
        }

        prop_compose! {
            pub(super) fn platform_strategy()(
                uuid in uuid()
            ) -> (Platform, Value) {
                let platform = Platform {
                    device_id: uuid.into(),
                };

                let expected_value = json!({
                    "2": {
                        "str": uuid.to_string(),
                    }
                });

                (platform, expected_value)
            }
        }
    }

    pub(super) mod request {
        use super::super::*;
        use crate::generators::context_strategy;
        use proptest::prelude::*;
        use serde_json::{json, Value};

        proptest! {
            #[test]
            fn test_new(ctx in context_strategy()) {
                let request = Request::new(&ctx);

                if ctx.canonical_url.is_none() {
                    prop_assert!(request.is_none());
                } else {
                    prop_assert!(request.is_some());

                    let request = request.unwrap();
                    let expected_url = &ctx.canonical_url.clone().unwrap();
                    prop_assert_eq!(expected_url, request.canonical_url.value);
                }
            }

            #[test]
            fn test_serialize((request, expected_value) in request_strategy()) {
                let serialized = serde_json::to_value(request).unwrap();
                prop_assert_eq!(expected_value, serialized);
            }
        }

        prop_compose! {
            pub(super) fn request_strategy()(
                canonical_url in ".*"
            ) -> (Request<'static>, Value) {
                let canonical_url_str: &'static str = Box::leak(canonical_url.clone().into_boxed_str());

                let request = Request {
                    canonical_url: canonical_url_str.into(),
                };

                let expected_value = json!({
                    "17": {
                        "str": canonical_url,
                    }
                });

                (request, expected_value)
            }
        }
    }

    pub(super) mod user {
        use super::super::*;
        use crate::generators::context_strategy;
        use prop::option;
        use proptest::prelude::*;
        use serde_json::{json, Value};

        proptest! {
            #[test]
            fn test_new(ctx in context_strategy()) {
                let user = User::new(&ctx);

                if ctx.user_id.is_none() {
                    prop_assert!(user.is_none());
                } else {
                    prop_assert!(user.is_some());

                    let user = user.unwrap();
                    prop_assert_eq!(ctx.user_id.as_ref().unwrap(), user.user_id.value);
                    prop_assert_eq!(ctx.logged_in, user.logged_in.map(|t| t.value));
                    prop_assert_eq!(ctx.cookie_created_timestamp, user.cookie_created_timestamp.map(|t| t.value));
                    prop_assert_eq!(ctx.user_is_employee, user.is_employee.map(|t| t.value));
                }
            }

            #[test]
            fn test_serialize((user, expected_value) in user_strategy()) {
                let serialized = serde_json::to_value(user.clone()).unwrap();

                prop_assert_eq!(expected_value, serialized);
            }
        }

        prop_compose! {
            pub(super) fn user_strategy()(
                user_id in ".*",
                logged_in in option::of(prop::bool::ANY),
                cookie_created_timestamp in option::of(prop::num::i64::ANY),
                is_employee in option::of(prop::bool::ANY)
            ) -> (User<'static>, Value) {
                let user_id_str: &'static str = Box::leak(user_id.clone().into_boxed_str());
                let user = User {
                    user_id: user_id_str.into(),
                    logged_in: logged_in.map(Thrifty::from),
                    cookie_created_timestamp: cookie_created_timestamp.map(Thrifty::from),
                    is_employee: is_employee.map(Thrifty::from),
                };

                let mut expected_value = json!({
                    "1": {
                        "str": user_id,
                    },
                });

                if let Some(liv) = logged_in {
                    expected_value.as_object_mut().unwrap().insert("3".to_string(), json!({
                        "tf": if liv { 1 } else { 0 }
                    }));
                }
                if let Some(cctv) = cookie_created_timestamp {
                    expected_value.as_object_mut().unwrap().insert("4".to_string(), json!({
                        "i64": cctv
                    }));
                }
                if let Some(iev) = is_employee {
                    expected_value.as_object_mut().unwrap().insert("16".to_string(), json!({
                        "tf": if iev { 1 } else { 0 }
                    }));
                }

                (user, expected_value)
            }
        }
    }

    pub(super) mod experiment {
        use super::super::*;
        use super::experiment_event::experiment_event_strategy;
        use super::*;
        use crate::generators::bucketing_field;
        use serde_json::{json, Value};

        proptest! {
            #[test]
            fn test_try_from_invalid_start(mut event in experiment_event_strategy(), start_ts in (i64::MAX as u64)..) {
                event.start_ts = start_ts;

                let exp_res = Experiment::try_from(event);
                prop_assert!(exp_res.is_err());
            }

            #[test]
            fn test_try_from_invalid_stop(mut event in experiment_event_strategy(), stop_ts in (i64::MAX as u64)..) {
                event.stop_ts = stop_ts;

                let exp_res = Experiment::try_from(event);
                prop_assert!(exp_res.is_err());
            }

            #[test]
            fn test_try_from(event in experiment_event_strategy()) {
                let exp = Experiment::try_from(event.clone());
                prop_assert!(exp.is_ok());

                let exp = exp.unwrap();
                prop_assert_eq!(event.feature_id, exp.experiment_id.value as u32);
                prop_assert_eq!(event.feature_name, exp.name.value);
                prop_assert_eq!(event.owner, exp.owner.value);
                prop_assert_eq!(event.variant_name, exp.variant.value);
                prop_assert_eq!(event.start_ts, exp.start_ts.value as u64);
                prop_assert_eq!(event.stop_ts, exp.stop_ts.value as u64);
                prop_assert_eq!(event.bucketing_field.to_string(), exp.bucketing_key.value);
                prop_assert_eq!(event.feature_version.to_string(), exp.version.value);
                prop_assert_eq!(event.bucketing_value, exp.bucketing_value.value);
                prop_assert_eq!(event.decision_kind == DecisionKind::Override, exp.is_override.value);
            }

            #[test]
            fn test_serialize((exp, expected_value) in experiment_strategy()) {
                let serialized = serde_json::to_value(exp).unwrap();
                prop_assert_eq!(expected_value, serialized);
            }
        }

        prop_compose! {
            pub(super) fn experiment_strategy()(
                experiment_id in prop::num::i64::ANY,
                name in ".*",
                owner in ".*",
                variant in ".*",
                start_ts in prop::num::i64::ANY,
                stop_ts in prop::num::i64::ANY,
                bucketing_field in bucketing_field(),
                version in ".*",
                bucketing_value in ".*",
                is_override in prop::bool::ANY,
            ) -> (Experiment, Value) {
                let bucketing_key = bucketing_field.to_string();

                let exp = Experiment {
                    experiment_id: experiment_id.into(),
                    name: name.clone().into(),
                    owner: owner.clone().into(),
                    variant: variant.clone().into(),
                    start_ts: start_ts.into(),
                    stop_ts: stop_ts.into(),
                    bucketing_key: bucketing_key.clone().into(),
                    version: version.clone().into(),
                    bucketing_value: bucketing_value.clone().into(),
                    is_override: is_override.into(),
                };

                let expected_value = json!({
                    "1": {
                        "i64": experiment_id,
                    },
                    "2": {
                        "str": name,
                    },
                    "3": {
                        "str": owner,
                    },
                    "4": {
                        "str": variant,
                    },
                    "5": {
                        "i64": start_ts,
                    },
                    "6": {
                        "i64": stop_ts,
                    },
                    "7": {
                        "str": bucketing_key,
                    },
                    "8": {
                        "str": version,
                    },
                    "9": {
                        "str": bucketing_value,
                    },
                    "10": {
                        "tf": if is_override { 1 } else { 0 }
                    }
                });

                (exp, expected_value)
            }
        }
    }

    pub(super) mod geo {
        use super::super::*;
        use crate::generators::context_strategy;
        use proptest::prelude::*;
        use serde_json::{json, Value};

        proptest! {
            #[test]
            fn test_new(ctx in context_strategy()) {
                let geo = Geo::new(&ctx);

                if ctx.country_code.is_none() {
                    prop_assert!(geo.is_none());
                } else {
                    prop_assert!(geo.is_some());

                    let geo = geo.unwrap();
                    let expected_cc = &ctx.country_code.clone().unwrap();
                    prop_assert_eq!(expected_cc, geo.country_code.value);
                }
            }

            #[test]
            fn test_serialize((geo, expected_value) in geo_strategy()) {
                let serialized = serde_json::to_value(geo).unwrap();
                prop_assert_eq!(expected_value, serialized);
            }
        }

        prop_compose! {
            pub(super) fn geo_strategy()(
                country_code in ".*"
            ) -> (Geo<'static>, Value) {
                let country_code_str: &'static str = Box::leak(country_code.clone().into_boxed_str());

                let geo = Geo {
                    country_code: country_code_str.into(),
                };

                let expected_value = json!({
                    "1": {
                        "str": country_code,
                    },
                });

                (geo, expected_value)
            }
        }
    }

    pub(super) mod experiment_event {
        use super::*;
        use crate::generators::*;

        proptest! {
            #[test]
            fn test_to_string(event in experiment_event_strategy()) {
                let event_str = event.to_string();
                let mut tokens = event_str.split("::::");

                let dk = tokens.next().map(|sv| {
                    let uv = sv.parse::<u8>().unwrap();
                    DecisionKind::try_from(uv).unwrap()
                }).unwrap();
                prop_assert_eq!(event.decision_kind, dk);

                let feature_id = tokens.next().map(|sv| sv.parse::<u32>().unwrap()).unwrap();
                prop_assert_eq!(event.feature_id, feature_id);

                prop_assert_eq!(event.feature_name, tokens.next().unwrap());

                let feature_version = tokens.next().map(|sv| sv.parse::<u32>().unwrap()).unwrap();
                prop_assert_eq!(event.feature_version, feature_version);

                prop_assert_eq!(event.variant_name, tokens.next().unwrap());
                prop_assert_eq!(event.bucketing_value, tokens.next().unwrap());
                prop_assert_eq!(event.bucketing_field.to_string(), tokens.next().unwrap());

                let start_ts = tokens.next().map(|sv| sv.parse::<u64>().unwrap()).unwrap();
                prop_assert_eq!(event.start_ts, start_ts);

                let stop_ts = tokens.next().map(|sv| sv.parse::<u64>().unwrap()).unwrap();
                prop_assert_eq!(event.stop_ts, stop_ts);

                prop_assert_eq!(event.owner, tokens.next().unwrap());

                prop_assert!(tokens.next().is_none());
            }
        }

        prop_compose! {
            pub(super) fn experiment_event_strategy() (
                decision_kind in decision_kind(),
                feature_id in prop::num::u32::ANY,
                feature_name in "[^:]*",
                feature_version in prop::num::u32::ANY,
                variant_name in "[^:]*",
                bucketing_field in bucketing_field(),
                bucketing_value in "[^:]*",
                start_ts in 0u64..=(i64::MAX as u64),
                stop_ts in 0u64..=(i64::MAX as u64),
                owner in "[^:]*",
            ) -> ExperimentEvent {
                ExperimentEvent {
                    decision_kind,
                    feature_id,
                    feature_name,
                    feature_version,
                    variant_name,
                    bucketing_field,
                    bucketing_value,
                    start_ts,
                    stop_ts,
                    owner,
                }
            }
        }
    }

    mod event {
        use super::super::*;
        use super::*;
        use crate::generators::uuid;
        use prop::option;
        use serde_json::{json, Value};
        use std::str::FromStr;

        proptest! {
            #[test]
            fn test_serialize((event, expected_value) in event_strategy()) {
                let serialized = serde_json::to_value(event).unwrap();

                prop_assert_eq!(expected_value, serialized);
            }
        }

        prop_compose! {
            fn event_strategy()(
                client_timestamp in prop::num::i64::ANY,
                uuid in uuid(),
                correlation_id in uuid(),
                app_opt in option::of(app::app_strategy()),
                platform_opt in option::of(platform::platform_strategy()),
                request_opt in option::of(request::request_strategy()),
                user_opt in option::of(user::user_strategy()),
                (experiment, expected_exp_value) in experiment::experiment_strategy(),
                geo_opt in option::of(geo::geo_strategy()),
            ) -> (Event<'static>, Value) {
                let client_timestamp: &'static Thrifty<i64> = Box::leak(Box::new(client_timestamp.into()));
                let correlation_id: &'static Thrifty<Uuid> = Box::leak(Box::new(correlation_id.into()));

                let (noun, expected_noun_str) = match BucketingField::from_str(&experiment.bucketing_key.value).unwrap() {
                    BucketingField::UserId => (NOUN_USER_ID, "user_id"),
                    BucketingField::DeviceId => (NOUN_DEVICE_ID, "device_id"),
                    BucketingField::CanonicalUrl => (NOUN_CANONICAL_URL, "canonical_url"),
                };

                let (app, expected_app_value) = match app_opt {
                    Some((a, v)) => {
                        let boxed: &'static Option<Thrifty<App<'static>>> = Box::leak(Box::new(Some(a.into())));

                        (boxed, Some(v))
                    },
                    _ => (&None, None),
                };

                let (platform, expected_platform_value) = match platform_opt {
                    Some((p, v)) => {
                        let boxed: &'static Option<Thrifty<Platform>> = Box::leak(Box::new(Some(p.into())));

                        (boxed, Some(v))
                    },
                    _ => (&None, None),
                };

                let (request, expected_request_value) = match request_opt {
                    Some((r, v)) => {
                        let boxed: &'static Option<Thrifty<Request<'static>>> = Box::leak(Box::new(Some(r.into())));

                        (boxed, Some(v))
                    },
                    _ => (&None, None),
                };

                let (user, expected_user_value) = match user_opt {
                    Some((u, v)) => {
                        let boxed: &'static Option<Thrifty<User<'static>>> = Box::leak(Box::new(Some(u.into())));

                        (boxed, Some(v))
                    },
                    _ => (&None, None),
                };

                let (geo, expected_geo_value) = match geo_opt {
                    Some((g, v)) => {
                        let boxed: &'static Option<Thrifty<Geo<'static>>> = Box::leak(Box::new(Some(g.into())));

                        (boxed, Some(v))
                    },
                    _ => (&None, None),
                };

                let event = Event {
                    source: SOURCE,
                    action: ACTION,
                    noun,
                    client_timestamp,
                    uuid: uuid.into(),
                    correlation_id,
                    app,
                    platform,
                    request,
                    user,
                    experiment: experiment.into(),
                    geo,
                };

                let mut expected_value = json!({
                    "1": {
                        "str": "experiment",
                    },
                    "2": {
                        "str": "expose",
                    },
                    "3": {
                        "str": expected_noun_str,
                    },
                    "5": {
                        "i64": client_timestamp.value,
                    },
                    "6": {
                        "str": uuid.to_string(),
                    },
                    "8": {
                        "str": correlation_id.value.to_string(),
                    },
                    "129": {
                        "rec": expected_exp_value,
                    },
                });

                if let Some(eav) = expected_app_value {
                    expected_value.as_object_mut().unwrap().insert("107".to_string(), json!({
                        "rec": eav,
                    }));
                }
                if let Some(epv) = expected_platform_value {
                    expected_value.as_object_mut().unwrap().insert("108".to_string(), json!({
                        "rec": epv,
                    }));
                }
                if let Some(erv) = expected_request_value {
                    expected_value.as_object_mut().unwrap().insert("109".to_string(), json!({
                        "rec": erv,
                    }));
                }
                if let Some(euv) = expected_user_value {
                    expected_value.as_object_mut().unwrap().insert("112".to_string(), json!({
                        "rec": euv,
                    }));
                }
                if let Some(egv) = expected_geo_value {
                    expected_value.as_object_mut().unwrap().insert("500".to_string(), json!({
                        "rec": egv,
                    }));
                }

                (event, expected_value)
            }
        }
    }

    mod serialized_events {
        use super::super::*;
        use super::*;
        use crate::generators::context_strategy;
        use chrono::{TimeZone, Utc};
        use serde_json::{json, Map, Value};

        proptest! {
            #[test]
            fn test_new(
                ctx in context_strategy(),
                event in experiment_event::experiment_event_strategy(),
            ) {
                let now = Utc::now();
                let parsed_events = SerializedEvents::new(&ctx, vec![event.clone()]).unwrap();
                let expected_data_string = event.to_string();

                prop_assert_eq!(vec![expected_data_string], parsed_events.event_data);

                prop_assert_eq!(1, parsed_events.events.len());
                prop_assert_eq!(event.decision_kind, parsed_events.events[0].kind);
                let parsed: Value = serde_json::from_str(&parsed_events.events[0].json).unwrap();
                let jv: &Map<String, Value> = parsed.as_object().unwrap();

                prop_assert_eq!(&json!("experiment"), &jv["1"]["str"]);
                prop_assert_eq!(&json!("expose"), &jv["2"]["str"]);

                let actual_noun = &jv["3"]["str"];

                match event.bucketing_field {
                    BucketingField::UserId => prop_assert_eq!(&json!("user_id"), actual_noun),
                    BucketingField::DeviceId => prop_assert_eq!(&json!("device_id"), actual_noun),
                    BucketingField::CanonicalUrl => prop_assert_eq!(&json!("canonical_url"), actual_noun),
                };

                let event_ts = &jv["5"]["i64"].as_i64().unwrap();
                let event_time = Utc.timestamp_millis(*event_ts);
                prop_assert!((event_time - now).num_milliseconds().abs() < 1000);

                // UUIDs are unique, so just check for presence.
                prop_assert!(&jv["6"].get("str").is_some());
                prop_assert!(&jv["8"].get("str").is_some());

                // The substructs are tested independently, so we quickly check that the struct was
                // set correctly.
                match ctx.app_name {
                    Some(name) => prop_assert_eq!(&Value::from(name), &jv["107"]["rec"]["2"]["str"]),
                    None => prop_assert!(&jv.get("107").is_none()),
                }

                match ctx.device_id {
                    Some(id) => prop_assert_eq!(&Value::from(id), &jv["108"]["rec"]["2"]["str"]),
                    None => prop_assert!(&jv.get("108").is_none()),
                }

                match ctx.canonical_url {
                    Some(url) => prop_assert_eq!(&Value::from(url), &jv["109"]["rec"]["17"]["str"]),
                    None => prop_assert!(&jv.get("109").is_none()),
                }

                match ctx.user_id {
                    Some(id) => prop_assert_eq!(&Value::from(id), &jv["112"]["rec"]["1"]["str"]),
                    None => prop_assert!(&jv.get("112").is_none()),
                }

                match ctx.country_code {
                    Some(cc) => prop_assert_eq!(&Value::from(cc), &jv["500"]["rec"]["1"]["str"]),
                    None => prop_assert!(&jv.get("500").is_none()),
                }

                prop_assert_eq!(&Value::from(event.feature_id), &jv["129"]["rec"]["1"]["i64"]);
            }
        }
    }
}
