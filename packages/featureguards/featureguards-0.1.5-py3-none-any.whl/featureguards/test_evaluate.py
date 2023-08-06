import unittest
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from google.protobuf.timestamp_pb2 import Timestamp

from featureguards.common import FeatureToggleException
from featureguards.evaluate import hash, is_on, match
from featureguards.feature_toggles import Attrs
from featureguards.proto.shared.feature_toggle_pb2 import (
    BoolOp, DateTimeOp, FeatureToggle, FloatOp, IntOp, Key, Match,
    OnOffFeature, PercentageFeature, Stickiness, StringOp, Variant)

load_dotenv()

ATTRS: Attrs = {
    'user_id':
    123,
    'company_id':
    123,
    'company_slug':
    'FeatureGuards',
    'is_admin':
    True,
    'created_at':
    datetime.strptime('2019-10-12T07:20:50.52Z',
                      '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
}


class TestHashing(unittest.TestCase):

    def test_hash_float(self):
        v = hash('FOO', [Key(key='user_id', key_type=Key.FLOAT)], '', ATTRS)
        self.assertEqual(v, 4353148100880623749)
        self.assertRaisesRegex(
            FeatureToggleException,
            'expected float/int value for attribute company_slug and feature flag FOO',
            hash, 'FOO', [Key(key='company_slug', key_type=Key.FLOAT)], '',
            ATTRS)

    def test_hash_int(self):
        v = hash('FOO', [Key(key='company_id', key_type=Key.INT)], '', ATTRS)
        self.assertEqual(v, 4353148100880623749)

        v = hash('FOO', [Key(key='user_id', key_type=Key.INT)], '', ATTRS)
        self.assertEqual(v, 4353148100880623749)

    def test_hash_string(self):
        v = hash('FOO', [Key(key='company_slug', key_type=Key.STRING)], '',
                 ATTRS)
        self.assertEqual(v, 15324770540884756055)

        self.assertRaisesRegex(
            FeatureToggleException,
            'expected str value for attribute company_id and feature flag FOO',
            hash, 'FOO', [Key(key='company_id', key_type=Key.STRING)], '',
            ATTRS)

    def test_hash_string_with_salt(self):
        v = hash('FOO', [Key(key='company_slug', key_type=Key.STRING)], 'foo',
                 ATTRS)
        self.assertEqual(v, 13498803372803212218)

    def test_hash_string_with_different_salt(self):
        v = hash('FOO', [Key(key='company_slug', key_type=Key.STRING)], 'FoO',
                 ATTRS)
        self.assertEqual(v, 6440734465410601463)

    def test_hash_bool(self):
        v = hash('FOO', [Key(key='is_admin', key_type=Key.BOOLEAN)], '', ATTRS)
        self.assertEqual(v, 15549163119024811594)
        self.assertRaisesRegex(
            FeatureToggleException,
            'expected boolean value for attribute company_slug and feature flag FOO',
            hash, 'FOO', [Key(key='company_slug', key_type=Key.BOOLEAN)], '',
            ATTRS)

    def test_hash_datetime(self):
        v = hash('FOO', [Key(key='created_at', key_type=Key.DATE_TIME)], '',
                 ATTRS)
        self.assertEqual(v, 16092501893693493459)
        self.assertRaisesRegex(
            FeatureToggleException,
            'expected datetime value for attribute company_slug and feature flag FOO',
            hash, 'FOO', [Key(key='company_slug', key_type=Key.DATE_TIME)], '',
            ATTRS)

    def test_hash_invalid(self):
        self.assertRaisesRegex(
            FeatureToggleException, 'no matching attribute for FOO', hash,
            'FOO', [Key(key='created_at2', key_type=Key.DATE_TIME)], '', ATTRS)

        self.assertRaisesRegex(
            FeatureToggleException,
            'expected float/int value for attribute created_at and feature flag FOO',
            hash, 'FOO', [Key(key='created_at', key_type=Key.FLOAT)], '',
            ATTRS)


class TestStringMatch(unittest.TestCase):

    def test_match_eq(self):
        v = match('FOO', [
            Match(key=Key(key='company_slug', key_type=Key.STRING),
                  string_op=StringOp(op=StringOp.EQ, values=['FeatureGuards']))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_eq(self):
        v = match('FOO', [
            Match(key=Key(key='company_slug', key_type=Key.STRING),
                  string_op=StringOp(op=StringOp.EQ, values=['featureguards']))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_empty_eq(self):
        v = match('FOO', [
            Match(key=Key(key='company_slug', key_type=Key.STRING),
                  string_op=StringOp(op=StringOp.EQ, values=['']))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_contains(self):
        v = match('FOO', [
            Match(key=Key(key='company_slug', key_type=Key.STRING),
                  string_op=StringOp(op=StringOp.CONTAINS, values=['Guards']))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_contains(self):
        v = match('FOO', [
            Match(key=Key(key='company_slug', key_type=Key.STRING),
                  string_op=StringOp(op=StringOp.CONTAINS, values=['guards']))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_in(self):
        v = match('FOO', [
            Match(key=Key(key='company_slug', key_type=Key.STRING),
                  string_op=StringOp(op=StringOp.IN,
                                     values=['foo', 'FeatureGuards']))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_in(self):
        v = match('FOO', [
            Match(key=Key(key='company_slug', key_type=Key.STRING),
                  string_op=StringOp(op=StringOp.IN, values=['foo', 'Guards']))
        ], ATTRS)
        self.assertEqual(v, False)


class TestBooleanMatch(unittest.TestCase):

    def test_match_eq(self):
        v = match('FOO', [
            Match(key=Key(key='is_admin', key_type=Key.BOOLEAN),
                  bool_op=BoolOp(value=True))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_eq(self):
        v = match('FOO', [
            Match(key=Key(key='is_admin', key_type=Key.BOOLEAN),
                  bool_op=BoolOp(value=False))
        ], ATTRS)
        self.assertEqual(v, False)


class TestFloatMatch(unittest.TestCase):

    def test_match_eq(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.EQ, values=[123]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_eq(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.EQ, values=[1234]))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_neq(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.NEQ, values=[1234]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_eq(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.NEQ, values=[123]))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_gt(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.GT, values=[122]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_gt(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.GT, values=[123]))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_gte(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.GTE, values=[123]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_gte(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.GTE, values=[124]))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_lt(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.LT, values=[124]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_lt(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.LT, values=[123]))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_lte(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.LTE, values=[123]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_lte(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.LTE, values=[122]))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_in(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.IN, values=[-1, 2, 123]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_in(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.FLOAT),
                  float_op=FloatOp(op=FloatOp.IN, values=[0, 122]))
        ], ATTRS)
        self.assertEqual(v, False)


class TestIntMatch(unittest.TestCase):

    def test_match_eq(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.EQ, values=[123]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_eq(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.EQ, values=[1234]))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_neq(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.NEQ, values=[1234]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_eq(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.NEQ, values=[123]))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_gt(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.GT, values=[122]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_gt(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.GT, values=[123]))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_gte(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.GTE, values=[123]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_gte(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.GTE, values=[124]))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_lt(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.LT, values=[124]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_lt(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.LT, values=[123]))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_lte(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.LTE, values=[123]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_lte(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.LTE, values=[122]))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_in(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.IN, values=[-1, 2, 123]))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_in(self):
        v = match('FOO', [
            Match(key=Key(key='user_id', key_type=Key.INT),
                  int_op=IntOp(op=IntOp.IN, values=[0, 122]))
        ], ATTRS)
        self.assertEqual(v, False)


class TestDatetimeMatch(unittest.TestCase):

    def test_match_after(self):
        dt = ATTRS['created_at'] + timedelta(-1)
        val = Timestamp()
        val.FromDatetime(dt)
        v = match('FOO', [
            Match(key=Key(key='created_at', key_type=Key.DATE_TIME),
                  date_time_op=DateTimeOp(op=DateTimeOp.AFTER, timestamp=val))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_after(self):
        dt = ATTRS['created_at'] + timedelta(1)
        val = Timestamp()
        val.FromDatetime(dt)
        v = match('FOO', [
            Match(key=Key(key='created_at', key_type=Key.DATE_TIME),
                  date_time_op=DateTimeOp(op=DateTimeOp.AFTER, timestamp=val))
        ], ATTRS)
        self.assertEqual(v, False)

    def test_match_before(self):
        dt = ATTRS['created_at'] + timedelta(1)
        val = Timestamp()
        val.FromDatetime(dt)
        v = match('FOO', [
            Match(key=Key(key='created_at', key_type=Key.DATE_TIME),
                  date_time_op=DateTimeOp(op=DateTimeOp.BEFORE, timestamp=val))
        ], ATTRS)
        self.assertEqual(v, True)

    def test_mismatch_before(self):
        dt = ATTRS['created_at'] + timedelta(-1)
        val = Timestamp()
        val.FromDatetime(dt)
        v = match('FOO', [
            Match(key=Key(key='created_at', key_type=Key.DATE_TIME),
                  date_time_op=DateTimeOp(op=DateTimeOp.BEFORE, timestamp=val))
        ], ATTRS)
        self.assertEqual(v, False)


class TestIsOnForOnOff(unittest.TestCase):

    def test_off_for_deleted(self):
        dt = Timestamp()
        dt.FromDatetime(datetime.now())
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.ON_OFF,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          deleted_at=dt,
                          on_off=OnOffFeature(on=Variant(weight=100,
                                                         matches=[]),
                                              off=Variant(weight=0,
                                                          matches=[]))), ATTRS)
        self.assertEqual(v, False)

    def test_off_for_disabled(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=False,
                          toggle_type=FeatureToggle.Type.ON_OFF,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          on_off=OnOffFeature(on=Variant(weight=100,
                                                         matches=[]),
                                              off=Variant(weight=0,
                                                          matches=[]))), ATTRS)
        self.assertEqual(v, False)

    def test_is_on(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.ON_OFF,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          on_off=OnOffFeature(on=Variant(weight=100,
                                                         matches=[]),
                                              off=Variant(weight=0,
                                                          matches=[]))), ATTRS)
        self.assertEqual(v, True)

    def test_raises_partial_weights(self):
        self.assertRaisesRegex(
            FeatureToggleException, 'feature flag FOO has invalid weights',
            is_on,
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.ON_OFF,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          on_off=OnOffFeature(on=Variant(weight=99,
                                                         matches=[]),
                                              off=Variant(weight=1,
                                                          matches=[]))), ATTRS)

    def test_raises_for_equal_weights(self):
        self.assertRaisesRegex(
            FeatureToggleException, 'feature flag FOO has invalid weights',
            is_on,
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.ON_OFF,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          on_off=OnOffFeature(on=Variant(weight=0, matches=[]),
                                              off=Variant(weight=0,
                                                          matches=[]))), ATTRS)

    def test_is_off(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.ON_OFF,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          on_off=OnOffFeature(on=Variant(weight=0, matches=[]),
                                              off=Variant(weight=100,
                                                          matches=[]))), ATTRS)
        self.assertEqual(v, False)

    def test_is_on_based_on_allowlist(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.ON_OFF,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          on_off=OnOffFeature(on=Variant(
                              weight=0,
                              matches=[
                                  Match(key=Key(key='user_id',
                                                key_type=Key.FLOAT),
                                        float_op=FloatOp(op=FloatOp.EQ,
                                                         values=[123]))
                              ]),
                                              off=Variant(weight=100,
                                                          matches=[]))), ATTRS)
        self.assertEqual(v, True)

    def test_is_off_based_on_allowlist(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.ON_OFF,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          on_off=OnOffFeature(on=Variant(
                              weight=0,
                              matches=[
                                  Match(key=Key(key='user_id',
                                                key_type=Key.FLOAT),
                                        float_op=FloatOp(op=FloatOp.EQ,
                                                         values=[1234]))
                              ]),
                                              off=Variant(weight=100,
                                                          matches=[]))), ATTRS)
        self.assertEqual(v, False)

    def test_is_off_based_on_disallowlist(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.ON_OFF,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          on_off=OnOffFeature(
                              on=Variant(weight=100, matches=[]),
                              off=Variant(
                                  weight=0,
                                  matches=[
                                      Match(key=Key(key='user_id',
                                                    key_type=Key.FLOAT),
                                            float_op=FloatOp(op=FloatOp.EQ,
                                                             values=[123]))
                                  ]))), ATTRS)
        self.assertEqual(v, False)


class TestIsOnForPercentage(unittest.TestCase):

    def test_on_for_random(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.PERCENTAGE,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          percentage=PercentageFeature(
                              stickiness=Stickiness(
                                  stickiness_type=Stickiness.Type.RANDOM),
                              on=Variant(weight=100, matches=[]),
                              off=Variant(weight=0, matches=[]))), ATTRS)
        self.assertEqual(v, True)

    def test_off_for_random(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.PERCENTAGE,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          percentage=PercentageFeature(
                              stickiness=Stickiness(
                                  stickiness_type=Stickiness.Type.RANDOM),
                              on=Variant(weight=0, matches=[]),
                              off=Variant(weight=100, matches=[]))), ATTRS)
        self.assertEqual(v, False)

    def test_on_for_sticky_with_70_percent(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.PERCENTAGE,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          percentage=PercentageFeature(stickiness=Stickiness(
                              stickiness_type=Stickiness.Type.KEYS,
                              keys=[Key(key='user_id', key_type=Key.FLOAT)]),
                                                       on=Variant(weight=70,
                                                                  matches=[]),
                                                       off=Variant(
                                                           weight=30,
                                                           matches=[]))),
            ATTRS)
        self.assertEqual(v, True)

    def test_off_for_sticky_with_60_percent(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.PERCENTAGE,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          percentage=PercentageFeature(stickiness=Stickiness(
                              stickiness_type=Stickiness.Type.KEYS,
                              keys=[Key(key='user_id', key_type=Key.FLOAT)]),
                                                       on=Variant(weight=60,
                                                                  matches=[]),
                                                       off=Variant(
                                                           weight=40,
                                                           matches=[]))),
            ATTRS)
        self.assertEqual(v, False)

    def test_raises_for_equal_weights(self):
        self.assertRaisesRegex(
            FeatureToggleException, 'feature flag FOO has invalid weights',
            is_on,
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.PERCENTAGE,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          percentage=PercentageFeature(
                              stickiness=Stickiness(
                                  stickiness_type=Stickiness.Type.RANDOM),
                              on=Variant(weight=0, matches=[]),
                              off=Variant(weight=0, matches=[]))), ATTRS)

    def test_is_on_based_on_allowlist(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.PERCENTAGE,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          percentage=PercentageFeature(
                              stickiness=Stickiness(
                                  stickiness_type=Stickiness.Type.RANDOM),
                              on=Variant(weight=0,
                                         matches=[
                                             Match(key=Key(key='user_id',
                                                           key_type=Key.FLOAT),
                                                   float_op=FloatOp(
                                                       op=FloatOp.EQ,
                                                       values=[123]))
                                         ]),
                              off=Variant(weight=100, matches=[]))), ATTRS)
        self.assertEqual(v, True)

    def test_is_off_based_on_allowlist(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.PERCENTAGE,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          percentage=PercentageFeature(
                              stickiness=Stickiness(
                                  stickiness_type=Stickiness.Type.RANDOM),
                              on=Variant(weight=0,
                                         matches=[
                                             Match(key=Key(key='user_id',
                                                           key_type=Key.FLOAT),
                                                   float_op=FloatOp(
                                                       op=FloatOp.EQ,
                                                       values=[1234]))
                                         ]),
                              off=Variant(weight=100, matches=[]))), ATTRS)
        self.assertEqual(v, False)

    def test_is_off_based_on_disallowlist(self):
        v = is_on(
            FeatureToggle(name='FOO',
                          enabled=True,
                          toggle_type=FeatureToggle.Type.PERCENTAGE,
                          id='123',
                          project_id='proj1234',
                          description='',
                          version=1,
                          platforms=[],
                          percentage=PercentageFeature(
                              stickiness=Stickiness(
                                  stickiness_type=Stickiness.Type.RANDOM),
                              on=Variant(weight=100, matches=[]),
                              off=Variant(
                                  weight=0,
                                  matches=[
                                      Match(key=Key(key='user_id',
                                                    key_type=Key.FLOAT),
                                            float_op=FloatOp(op=FloatOp.EQ,
                                                             values=[123]))
                                  ]))), ATTRS)
        self.assertEqual(v, False)


if __name__ == '__main__':
    unittest.main()
