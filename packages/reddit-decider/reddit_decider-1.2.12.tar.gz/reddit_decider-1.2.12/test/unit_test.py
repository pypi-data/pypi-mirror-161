#!/usr/bin/env python
import os

from contextlib import contextmanager
from unittest import TestCase

import rust_decider

from utils import create_temp_config_file

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


def setup_decider(cfg_path):
    return rust_decider.init(
        "darkmode overrides targeting holdout mutex_group fractional_availability value",
        cfg_path,
    )


class TestDeciderPy(TestCase):
    valid_ctx_dict = {
        "user_id": "795244",
        "device_id": "1234",
        "canonical_url": "www.reddit.com",
        "locale": "us_en",
        "user_is_employee": True,
        "logged_in": None,
        "app_name": "ios",
        "build_number": 1234,
        "country_code": "UA",
        "origin_service": "oss",
        "auth_client_id": "test",
        "cookie_created_timestamp": 1648859753,
    }

    variants = [
        {"range_start": 0.0, "range_end": 0.2, "name": "control_1"},
        {"range_start": 0.2, "range_end": 0.4, "name": "variant_2"},
        {"range_start": 0.4, "range_end": 0.6, "name": "variant_3"},
        {"range_start": 0.6, "range_end": 0.8, "name": "variant_4"},
        {"range_start": 0.8, "range_end": 1.0, "name": "variant_5"},
    ]

    device_id_exp = {
        "genexp_device_id": {
            "id": 6222,
            "name": "genexp_device_id",
            "enabled": True,
            "owner": "test",
            "version": "5",
            "type": "range_variant",
            "start_ts": 0,
            "stop_ts": 2147483648,
            "emit_event": True,
            "experiment": {
                "variants": variants,
                "experiment_version": 5,
                "shuffle_version": 91,
                "bucket_val": "device_id",
                "log_bucketing": False,
            },
        }
    }

    canonical_url_exp = {
        "genexp_canonical_url": {
            "id": 6233,
            "name": "genexp_canonical_url",
            "enabled": True,
            "owner": "test",
            "version": "5",
            "type": "range_variant",
            "start_ts": 0,
            "stop_ts": 2147483648,
            "emit_event": True,
            "experiment": {
                "variants": variants,
                "experiment_version": 5,
                "shuffle_version": 91,
                "bucket_val": "canonical_url",
                "log_bucketing": False,
            },
        }
    }

    def setUp(self):
        super().setUp()
        self.ctx = rust_decider.make_ctx(self.valid_ctx_dict)
        self.genexp_0_cfg = {
            "genexp_0": {
                "id": 6299,
                "name": "genexp_0",
                "enabled": True,
                "owner": "test",
                "version": "5",
                "emit_event": True,
                "type": "range_variant",
                "start_ts": 0,
                "stop_ts": 2147483648,
                "experiment": {
                    "variants": self.variants,
                    "experiment_version": 5,
                    "shuffle_version": 91,
                    "bucket_val": "user_id",
                    "log_bucketing": False,
                },
            },
        }
        self.additional_2_exp = {
            "exp_0": {
                "id": 3248,
                "name": "exp_0",
                "enabled": True,
                "owner": "test",
                "version": "2",
                "type": "range_variant",
                "emit_event": True,
                "start_ts": 37173982,
                "stop_ts": 2147483648,
                "experiment": {
                    "variants": [
                        {"range_start": 0.0, "range_end": 0.2, "name": "control_1"},
                        {"range_start": 0.2, "range_end": 0.4, "name": "control_2"},
                        {"range_start": 0.4, "range_end": 0.6, "name": "variant_2"},
                        {"range_start": 0.6, "range_end": 0.8, "name": "variant_3"},
                        {"range_start": 0.8, "range_end": 1.0, "name": "variant_4"},
                    ],
                    "experiment_version": 2,
                    "shuffle_version": 91,
                    "bucket_val": "user_id",
                    "log_bucketing": False,
                },
            },
            "exp_1": {
                "id": 3246,
                "name": "exp_1",
                "enabled": True,
                "owner": "test",
                "version": "2",
                "type": "range_variant",
                "emit_event": True,
                "start_ts": 37173982,
                "stop_ts": 2147483648,
                "experiment": {
                    "variants": [
                        {"range_start": 0, "range_end": 0, "name": "variant_0"}
                    ],
                    "experiment_version": 2,
                    "shuffle_version": 0,
                    "bucket_val": "user_id",
                    "log_bucketing": False,
                },
            },
        }

    def test_init(self):
        # handles full cfg.json file
        decider = setup_decider(f"{TEST_DIR}/../../cfg.json")
        self.assertEqual(decider.err(), None)

    def test_init_bad_cfg(self):
        # an experiment's id is string instead of int
        cfg = {
            "exp_0": {
                "id": "3248",
                "name": "exp_0",
                "enabled": True,
                "owner": "test",
                "version": "2",
                "type": "range_variant",
                "start_ts": 37173982,
                "stop_ts": 2147483648,
                "experiment": {
                    "variants": [],
                    "experiment_version": 2,
                    "shuffle_version": 91,
                    "bucket_val": "user_id",
                    "log_bucketing": False,
                },
            }
        }

        with create_temp_config_file(cfg) as f:
            decider = setup_decider(f.name)
            assert (
                'Decider initialization failed: Json error: "invalid type: string \\"3248\\"'
                in decider.err()
            )

    def test_make_ctx(self):
        ctx = rust_decider.make_ctx(self.valid_ctx_dict)
        self.assertEqual(ctx.err(), None)

    def test_make_ctx_string_type_mismatch(self):
        str_fields = [
            "locale",
            "country_code",
            "app_name",
            "device_id",
            "canonical_url",
            "origin_service",
            "auth_client_id",
        ]
        for str_field in str_fields:
            v_ctx = self.valid_ctx_dict.copy()
            v_ctx[str_field] = 1
            ctx = rust_decider.make_ctx(v_ctx)
            self.assertEqual(f'"{str_field}" type mismatch (string).', ctx.err())

    def test_make_ctx_bool_type_mismatch(self):
        bool_fields = ["logged_in", "user_is_employee"]
        for bool_field in bool_fields:
            v_ctx = self.valid_ctx_dict.copy()
            v_ctx[bool_field] = "not bool"
            ctx = rust_decider.make_ctx(v_ctx)
            self.assertEqual(f'"{bool_field}" type mismatch (bool).', ctx.err())

    def test_make_ctx_int_type_mismatch(self):
        int_fields = ["build_number", "cookie_created_timestamp"]
        for int_field in int_fields:
            v_ctx = self.valid_ctx_dict.copy()
            v_ctx[int_field] = "not int"
            ctx = rust_decider.make_ctx(v_ctx)
            self.assertEqual(f'"{int_field}" type mismatch (integer).', ctx.err())

    # todo:
    # def test_make_ctx_without_user_id(self):

    # todo:
    # def test_make_ctx_with_None_fields(self):

    def test_choose(self):
        with create_temp_config_file(self.genexp_0_cfg) as f:
            decider = setup_decider(f.name)

            choice = decider.choose("genexp_0", self.ctx)

            self.assertEqual(choice.err(), None)
            self.assertEqual(choice.decision(), "variant_5")
            self.assertEqual(
                choice.events(),
                [
                    "0::::6299::::genexp_0::::5::::variant_5::::795244::::user_id::::0::::2147483648::::test"
                ],
            )

    def test_choose_bad_init(self):
        decider = rust_decider.init("foo", "bah")
        choice = decider.choose("bar", self.ctx)

        self.assertEqual(choice.err(), "Decider not found.")

    def test_choose_bucket_val_device_id(self):
        with create_temp_config_file(self.device_id_exp) as f:
            decider = setup_decider(f.name)

            choice = decider.choose("genexp_device_id", self.ctx)

            self.assertEqual(choice.err(), None)
            self.assertEqual(choice.decision(), "variant_5")

    def test_choose_bucket_val_device_id_missing_identifier(self):
        with create_temp_config_file(self.device_id_exp) as f:
            decider = setup_decider(f.name)
            ctx = self.valid_ctx_dict.copy()
            del ctx["device_id"]
            missing_device_id_ctx = rust_decider.make_ctx(ctx)

            choice = decider.choose("genexp_device_id", missing_device_id_ctx)

            self.assertEqual(
                choice.err(),
                'Missing field "device_id" in context for bucket_val = device_id',
            )
            self.assertEqual(choice.decision(), None)

    def test_choose_bucket_val_canonical_url(self):
        with create_temp_config_file(self.canonical_url_exp) as f:
            decider = setup_decider(f.name)

            choice = decider.choose("genexp_canonical_url", self.ctx)

            self.assertEqual(choice.err(), None)
            self.assertEqual(choice.decision(), "control_1")

    def test_choose_bucket_val_canonical_url_missing_identifier(self):
        with create_temp_config_file(self.canonical_url_exp) as f:
            decider = setup_decider(f.name)
            ctx = self.valid_ctx_dict.copy()
            del ctx["canonical_url"]
            missing_canonical_url_ctx = rust_decider.make_ctx(ctx)

            choice = decider.choose("genexp_canonical_url", missing_canonical_url_ctx)

            self.assertEqual(
                choice.err(),
                'Missing field "canonical_url" in context for bucket_val = canonical_url',
            )
            self.assertEqual(choice.decision(), None)

    def test_choose_bucket_val_canonical_url_with_identifer_type(self):
        with create_temp_config_file(self.canonical_url_exp) as f:
            decider = setup_decider(f.name)

            choice = decider.choose(
                feature_name="genexp_canonical_url",
                ctx=self.ctx,
                identifier_type="canonical_url",
            )

            self.assertEqual(choice.err(), None)
            self.assertEqual(choice.decision(), "control_1")

    def test_choose_bucket_val_canonical_url_with_mismatched_identifer_type(self):
        with create_temp_config_file(self.canonical_url_exp) as f:
            decider = setup_decider(f.name)

            choice = decider.choose(
                feature_name="genexp_canonical_url",
                ctx=self.ctx,
                identifier_type="device_id",
            )

            self.assertEqual(
                choice.err(),
                'Requested identifier_type: "device_id" is incompatible with experiment\'s bucket_val = canonical_url.',
            )
            self.assertEqual(choice.decision(), None)

    def test_choose_bucket_val_canonical_url_with_incorrect_identifer_type(self):
        with create_temp_config_file(self.canonical_url_exp) as f:
            decider = setup_decider(f.name)

            choice = decider.choose(
                feature_name="genexp_canonical_url",
                ctx=self.ctx,
                identifier_type="blah",
            )

            self.assertEqual(
                choice.err(), 'identifier_type: "blah" is not a supported bucket_val.'
            )
            self.assertEqual(choice.decision(), None)

    def test_choose_with_other_fields_for_targeting(self):
        cfg = self.genexp_0_cfg.copy()
        cfg["genexp_0"]["experiment"].update(
            {"targeting": {"ALL": [{"EQ": {"field": "foo", "values": ["bar"]}}]}}
        )

        with create_temp_config_file(cfg) as f:
            decider = setup_decider(f.name)
            py_dict = self.valid_ctx_dict.copy()

            # targeting matches
            py_dict.update({"other_fields": {"foo": "bar"}})
            ctx = rust_decider.make_ctx(py_dict)

            choice = decider.choose("genexp_0", ctx)

            self.assertEqual(choice.err(), None)
            self.assertEqual(choice.decision(), "variant_5")
            self.assertEqual(
                choice.events(),
                [
                    "0::::6299::::genexp_0::::5::::variant_5::::795244::::user_id::::0::::2147483648::::test"
                ],
            )

            # targeting doesn't match
            py_dict.update({"other_fields": {"foo": "huh"}})
            ctx = rust_decider.make_ctx(py_dict)

            choice = decider.choose("genexp_0", ctx)
            self.assertEqual(choice.decision(), None)

    @contextmanager
    def test_feature_not_found(self):
        with create_temp_config_file({}) as f:
            decider = setup_decider(f.name)
            yield decider

    def test_choose_feature_not_found(self):
        with self.test_feature_not_found() as d:
            result = d.choose("any", self.ctx)

        self.assertEqual(result.err(), 'Feature "any" not found.')

    def test_choose_all(self):
        self.genexp_0_cfg.update(self.additional_2_exp)

        with create_temp_config_file(self.genexp_0_cfg) as f:
            decider = setup_decider(f.name)

            choice_res = decider.choose_all(self.ctx)

            assert choice_res.err() is None
            choice_dict = choice_res.decisions()

            # assert genexp_0
            self.assertEqual(len(choice_dict), len(self.genexp_0_cfg))
            self.assertEqual(
                choice_dict["genexp_0"].decision_dict(),
                {
                    "name": "variant_5",
                    "version": "5",
                    "id": "6299",
                    "experimentName": "genexp_0",
                },
            )
            self.assertEqual(
                choice_dict["genexp_0"].events(),
                [
                    "0::::6299::::genexp_0::::5::::variant_5::::795244::::user_id::::0::::2147483648::::test"
                ],
            )

            # assert exp_0
            self.assertEqual(
                choice_dict["exp_0"].decision_dict(),
                {
                    "name": "variant_3",
                    "version": "2",
                    "id": "3248",
                    "experimentName": "exp_0",
                },
            )
            self.assertEqual(
                choice_dict["exp_0"].events(),
                [
                    "0::::3248::::exp_0::::2::::variant_3::::795244::::user_id::::37173982::::2147483648::::test"
                ],
            )

            # assert exp_1
            self.assertEqual(choice_dict["exp_1"].decision_dict(), {})
            self.assertEqual(choice_dict["exp_1"].events(), [])

    def test_choose_all_with_single_identifier_type(self):
        self.genexp_0_cfg.update(self.additional_2_exp)
        self.genexp_0_cfg.update(self.canonical_url_exp)

        with create_temp_config_file(self.genexp_0_cfg) as f:
            decider = setup_decider(f.name)

            choice_res = decider.choose_all(self.ctx, identifier_type="canonical_url")

            assert choice_res.err() is None
            choice_dict = choice_res.decisions()

            # assert canonical_url_exp
            self.assertEqual(len(choice_dict), 1)
            self.assertEqual(
                choice_dict["genexp_canonical_url"].decision_dict(),
                {
                    "name": "control_1",
                    "version": "5",
                    "id": "6233",
                    "experimentName": "genexp_canonical_url",
                },
            )
            self.assertEqual(
                choice_dict["genexp_canonical_url"].events(),
                [
                    "0::::6233::::genexp_canonical_url::::5::::control_1::::www.reddit.com::::canonical_url::::0::::2147483648::::test"
                ],
            )

    def test_get_bool(self):
        bool_val = True
        cfg = {
            "dc_bool": {
                "id": 3393,
                "value": bool_val,
                "type": "dynamic_config",
                "version": "2",
                "enabled": True,
                "owner": "test",
                "name": "dc_bool",
                "value_type": "Boolean",
                "experiment": {"experiment_version": 2},
            }
        }
        with create_temp_config_file(cfg) as f:
            decider = setup_decider(f.name)

            choice = decider.get_bool("dc_bool", self.ctx)

            self.assertEqual(choice.err(), None)
            self.assertEqual(choice.val(), bool_val)

    def test_get_bool_bad_init(self):
        decider = rust_decider.init("foo", "bah")
        dc = decider.get_bool("bar", self.ctx)

        self.assertEqual(dc.err(), "Decider not found.")

    def test_get_bool_feature_not_found(self):
        with self.test_feature_not_found() as d:
            result = d.get_bool("any", self.ctx)

        self.assertEqual(result.err(), 'Feature "any" not found.')

    def test_get_int(self):
        int_val = 99
        cfg = {
            "dc_int": {
                "id": 4393,
                "value": int_val,
                "type": "dynamic_config",
                "version": "2",
                "enabled": True,
                "owner": "test",
                "name": "dc_int",
                "value_type": "Integer",
                "experiment": {"experiment_version": 3},
            }
        }
        with create_temp_config_file(cfg) as f:
            decider = setup_decider(f.name)

            choice = decider.get_int("dc_int", self.ctx)

            self.assertEqual(choice.err(), None)
            self.assertEqual(choice.val(), int_val)

    def test_get_int_bad_init(self):
        decider = rust_decider.init("foo", "bah")
        dc = decider.get_int("bar", self.ctx)

        self.assertEqual(dc.err(), "Decider not found.")

    def test_get_int_feature_not_found(self):
        with self.test_feature_not_found() as d:
            result = d.get_int("any", self.ctx)

        self.assertEqual(result.err(), 'Feature "any" not found.')

    def test_get_float(self):
        float_val = 3.2
        cfg = {
            "dc_float": {
                "id": 5393,
                "value": float_val,
                "type": "dynamic_config",
                "version": "2",
                "enabled": True,
                "owner": "test",
                "name": "dc_float",
                "value_type": "Float",
                "experiment": {"experiment_version": 4},
            }
        }
        with create_temp_config_file(cfg) as f:
            decider = setup_decider(f.name)

            choice = decider.get_float("dc_float", self.ctx)

            self.assertEqual(choice.err(), None)
            self.assertEqual(choice.val(), float_val)

    def test_get_float_bad_init(self):
        decider = rust_decider.init("foo", "bah")
        dc = decider.get_float("bar", self.ctx)

        self.assertEqual(dc.err(), "Decider not found.")

    def test_get_float_feature_not_found(self):
        with self.test_feature_not_found() as d:
            result = d.get_float("any", self.ctx)

        self.assertEqual(result.err(), 'Feature "any" not found.')

    def test_get_string(self):
        string_val = "some_string"
        cfg = {
            "dc_string": {
                "id": 6393,
                "value": string_val,
                "type": "dynamic_config",
                "version": "2",
                "enabled": True,
                "owner": "test",
                "name": "dc_string",
                "value_type": "String",
                "experiment": {"experiment_version": 5},
            }
        }
        with create_temp_config_file(cfg) as f:
            decider = setup_decider(f.name)

            choice = decider.get_string("dc_string", self.ctx)

            self.assertEqual(choice.err(), None)
            self.assertEqual(choice.val(), string_val)

    def test_get_string_bad_init(self):
        decider = rust_decider.init("foo", "bah")
        dc = decider.get_string("bar", self.ctx)

        self.assertEqual(dc.err(), "Decider not found.")

    def test_get_string_feature_not_found(self):
        with self.test_feature_not_found() as d:
            result = d.get_string("any", self.ctx)

        self.assertEqual(result.err(), 'Feature "any" not found.')

    def test_get_map(self):
        map_val = {
            "v": {"nested_map": {"w": True, "x": 1, "y": "some_string", "z": 3.0}},
            "w": False,
            "x": 1,
            "y": "some_string",
            "z": 3.0,
        }
        cfg = {
            "dc_map": {
                "id": 1000000,
                "value": map_val,
                "type": "dynamic_config",
                "version": "1",
                "enabled": True,
                "owner": "test",
                "name": "dc_map",
                "value_type": "Map",
                "experiment": {"experiment_version": 1},
            }
        }
        with create_temp_config_file(cfg) as f:
            decider = setup_decider(f.name)

            choice = decider.get_map("dc_map", self.ctx)

            self.assertEqual(choice.err(), None)
            self.assertEqual(choice.val(), map_val)

    def test_get_map_bad_init(self):
        decider = rust_decider.init("foo", "bah")
        dc = decider.get_map("bar", self.ctx)

        self.assertEqual(dc.err(), "Decider not found.")

    def test_get_map_feature_not_found(self):
        with self.test_feature_not_found() as d:
            result = d.get_map("any", self.ctx)

        self.assertEqual(result.err(), 'Feature "any" not found.')

    def test_get_all_values(self):
        bool_val = True
        cfg_bool = {
            "dc_bool": {
                "id": 3393,
                "value": bool_val,
                "type": "dynamic_config",
                "version": "2",
                "enabled": True,
                "owner": "test",
                "name": "dc_bool",
                "value_type": "Boolean",
                "experiment": {"experiment_version": 2},
            }
        }
        cfg_missing_bool = {}
        cfg_missing_bool["dc_missing_bool"] = cfg_bool["dc_bool"].copy()
        cfg_missing_bool["dc_missing_bool"].update(
            {"value": None, "name": "dc_missing_bool"}
        )

        int_val = 99
        cfg_int = {
            "dc_int": {
                "id": 4393,
                "value": int_val,
                "type": "dynamic_config",
                "version": "2",
                "enabled": True,
                "owner": "test",
                "name": "dc_int",
                "value_type": "Integer",
                "experiment": {"experiment_version": 3},
            }
        }
        cfg_missing_int = {}
        cfg_missing_int["dc_missing_int"] = cfg_int["dc_int"].copy()
        cfg_missing_int["dc_missing_int"].update(
            {"value": None, "name": "dc_missing_int"}
        )

        float_val = 3.2
        cfg_float = {
            "dc_float": {
                "id": 5393,
                "value": float_val,
                "type": "dynamic_config",
                "version": "2",
                "enabled": True,
                "owner": "test",
                "name": "dc_float",
                "value_type": "Float",
                "experiment": {"experiment_version": 4},
            }
        }
        cfg_missing_float = {}
        cfg_missing_float["dc_missing_float"] = cfg_float["dc_float"].copy()
        cfg_missing_float["dc_missing_float"].update(
            {"value": None, "name": "dc_missing_float"}
        )

        string_val = "some_string"
        cfg_string = {
            "dc_string": {
                "id": 6393,
                "value": string_val,
                "type": "dynamic_config",
                "version": "2",
                "enabled": True,
                "owner": "test",
                "name": "dc_string",
                "value_type": "String",
                "experiment": {"experiment_version": 5},
            }
        }
        cfg_text = {
            "dc_text": {
                "id": 6393,
                "value": string_val,
                "type": "dynamic_config",
                "version": "2",
                "enabled": True,
                "owner": "test",
                "name": "dc_text",
                "value_type": "Text",
                "experiment": {"experiment_version": 5},
            }
        }
        cfg_missing_string = {}
        cfg_missing_string["dc_missing_string"] = cfg_string["dc_string"].copy()
        cfg_missing_string["dc_missing_string"].update(
            {"value": None, "name": "dc_missing_string"}
        )

        cfg_missing_text = {}
        cfg_missing_text["dc_missing_text"] = cfg_text["dc_text"].copy()
        cfg_missing_text["dc_missing_text"].update(
            {"value": None, "name": "dc_missing_text"}
        )

        map_val = {
            "v": {"nested_map": {"w": True, "x": 1, "y": "some_string", "z": 3.0}},
            "w": False,
            "x": 1,
            "y": "some_string",
            "z": 3.0,
        }
        cfg_map = {
            "dc_map": {
                "id": 1000000,
                "value": map_val,
                "type": "dynamic_config",
                "version": "1",
                "enabled": True,
                "owner": "test",
                "name": "dc_map",
                "value_type": "Map",
                "experiment": {"experiment_version": 1},
            }
        }
        cfg_missing_map = {}
        cfg_missing_map["dc_missing_map"] = cfg_map["dc_map"].copy()
        cfg_missing_map["dc_missing_map"].update(
            {"value": None, "name": "dc_missing_map"}
        )

        missing_value_type_cfg = {
            "dc_missing_value_type": {
                "id": 3393,
                "value": False,
                "type": "dynamic_config",
                "version": "2",
                "enabled": True,
                "owner": "test",
                "name": "dc_missing_value_type",
                "experiment": {"experiment_version": 2},
            }
        }

        self.genexp_0_cfg.update(cfg_bool)
        self.genexp_0_cfg.update(cfg_int)
        self.genexp_0_cfg.update(cfg_float)
        self.genexp_0_cfg.update(cfg_string)
        self.genexp_0_cfg.update(cfg_text)
        self.genexp_0_cfg.update(cfg_map)

        # should be set to default values
        self.genexp_0_cfg.update(cfg_missing_bool)
        self.genexp_0_cfg.update(cfg_missing_int)
        self.genexp_0_cfg.update(cfg_missing_float)
        self.genexp_0_cfg.update(cfg_missing_string)
        self.genexp_0_cfg.update(cfg_missing_text)
        self.genexp_0_cfg.update(cfg_missing_map)

        # missing "value_type" field
        self.genexp_0_cfg.update(missing_value_type_cfg)

        # should be excluded from result
        self.genexp_0_cfg.update(self.additional_2_exp)

        with create_temp_config_file(self.genexp_0_cfg) as f:
            decider = setup_decider(f.name)

            values_res = decider.get_all_values(self.ctx)

            self.assertEqual(values_res.err(), None)
            decisions_dict = values_res.decisions()

            # 6 correct DCs, 6 DCs w/ values set to respective defaults
            # 1 `missing_value_type_cfg` which sets "type" to empty string
            # (2 regular experiments are excluded)
            self.assertEqual(len(decisions_dict), 13)

            # test values get set
            bool_val_res = decisions_dict["dc_bool"]
            self.assertEqual(bool_val_res.err(), None)
            self.assertEqual(
                bool_val_res.value_dict(),
                {"name": "dc_bool", "value": bool_val, "type": "boolean"},
            )

            int_val_res = decisions_dict["dc_int"]
            self.assertEqual(int_val_res.err(), None)
            self.assertEqual(
                int_val_res.value_dict(),
                {"name": "dc_int", "value": int_val, "type": "integer"},
            )

            float_val_res = decisions_dict["dc_float"]
            self.assertEqual(float_val_res.err(), None)
            self.assertEqual(
                float_val_res.value_dict(),
                {"name": "dc_float", "value": float_val, "type": "float"},
            )

            string_val_res = decisions_dict["dc_string"]
            self.assertEqual(string_val_res.err(), None)
            self.assertEqual(
                string_val_res.value_dict(),
                {"name": "dc_string", "value": string_val, "type": "string"},
            )

            text_val_res = decisions_dict["dc_text"]
            self.assertEqual(text_val_res.err(), None)
            self.assertEqual(
                text_val_res.value_dict(),
                {"name": "dc_text", "value": string_val, "type": "string"},
            )

            map_val_res = decisions_dict["dc_map"]
            self.assertEqual(map_val_res.err(), None)
            self.assertEqual(
                map_val_res.value_dict(),
                {"name": "dc_map", "value": map_val, "type": "map"},
            )

            # test default values
            missing_bool_val_res = decisions_dict["dc_missing_bool"]
            self.assertEqual(missing_bool_val_res.err(), None)
            self.assertEqual(
                missing_bool_val_res.value_dict(),
                {"name": "dc_missing_bool", "value": False, "type": "boolean"},
            )

            missing_int_val_res = decisions_dict["dc_missing_int"]
            self.assertEqual(missing_int_val_res.err(), None)
            self.assertEqual(
                missing_int_val_res.value_dict(),
                {"name": "dc_missing_int", "value": 0, "type": "integer"},
            )

            missing_float_val_res = decisions_dict["dc_missing_float"]
            self.assertEqual(missing_float_val_res.err(), None)
            self.assertEqual(
                missing_float_val_res.value_dict(),
                {"name": "dc_missing_float", "value": 0.0, "type": "float"},
            )

            missing_string_val_res = decisions_dict["dc_missing_string"]
            self.assertEqual(missing_string_val_res.err(), None)
            self.assertEqual(
                missing_string_val_res.value_dict(),
                {"name": "dc_missing_string", "value": "", "type": "string"},
            )

            missing_text_val_res = decisions_dict["dc_missing_text"]
            self.assertEqual(missing_text_val_res.err(), None)
            self.assertEqual(
                missing_text_val_res.value_dict(),
                {"name": "dc_missing_text", "value": "", "type": "string"},
            )

            missing_map_val_res = decisions_dict["dc_missing_map"]
            self.assertEqual(missing_map_val_res.err(), None)
            self.assertEqual(
                missing_map_val_res.value_dict(),
                {"name": "dc_missing_map", "value": {}, "type": "map"},
            )

            # set "type" to empty string if "value_type" is missing on cfg
            missing_map_val_res = decisions_dict["dc_missing_value_type"]
            self.assertEqual(missing_map_val_res.err(), None)
            self.assertEqual(
                missing_map_val_res.value_dict(),
                {"name": "dc_missing_value_type", "value": False, "type": ""},
            )

    def test_get_experiment(self):
        with create_temp_config_file(self.genexp_0_cfg) as f:
            decider = setup_decider(f.name)

            experiment = decider.get_experiment("genexp_0")
            exp_dict = experiment.val()

            cfg = self.genexp_0_cfg["genexp_0"]
            expected_dict = {
                "id": cfg["id"],
                "name": cfg["name"],
                "enabled": cfg["enabled"],
                "type": "range_variant",
                "owner": cfg["owner"],
                "emit_event": cfg["emit_event"],
                "version": cfg["experiment"]["experiment_version"],
                "platform_bitmask": 0,
                "value": None,
                "value_type": None,
                "targeting": cfg.get("targeting"),
                "overrides": cfg.get("overrides"),
                "variant_set": {
                    "start_ts": cfg["start_ts"],
                    "stop_ts": cfg["stop_ts"],
                    "shuffle_version": cfg["experiment"]["shuffle_version"],
                    "bucket_val": cfg["experiment"]["bucket_val"],
                    "holdout": None,
                    "mutex_group": None,
                },
            }

            # pythonize() doesn't round range_start/range_end floats well
            # (e.g. 0.2 -> 0.20000000298023224)
            # but we don't use "variants" when calling `get_experiment()` in experiments.py SDK
            # so we ignore comparison here
            del exp_dict["variant_set"]["variants"]

            self.assertEqual(experiment.err(), None)
            self.assertDictEqual(exp_dict, expected_dict)

    def test_get_experiment_bad_init(self):
        decider = rust_decider.init("foo", "bah")
        exp = decider.get_experiment("bar")

        self.assertEqual(exp.err(), "Decider not found.")

    def test_get_experiment_feature_not_found(self):
        with self.test_feature_not_found() as d:
            result = d.get_experiment("any")

        self.assertEqual(result.err(), 'Feature "any" not found.')
