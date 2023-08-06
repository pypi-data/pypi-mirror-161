from datetime import datetime
from random import random
from typing import Optional, Sequence

from xxhash import xxh64_intdigest

from featureguards.common import Attrs, FeatureToggleException
from featureguards.proto.shared.feature_toggle_pb2 import (FeatureToggle, Key,
                                                           Match, Stickiness)


def is_on(ft: FeatureToggle, attrs: Optional[Attrs]) -> bool:
    if not ft.enabled:
        return False

    if ft.deleted_at and ft.deleted_at.ToNanoseconds() > 0:
        return False

    is_on = False
    if ft.toggle_type == FeatureToggle.Type.ON_OFF:
        on_off = ft.on_off
        if not on_off.on or not on_off.off:
            raise FeatureToggleException(f'feature flag {ft.name} is invalid')

        on = on_off.on
        off = on_off.off

        if (on.weight != 100 and on.weight != 0
                or off.weight != 100 and off.weight != 0
                or on.weight + off.weight != 100 or on.weight < 0
                or off.weight < 0):
            raise FeatureToggleException(
                f'feature flag {ft.name} has invalid weights')

        is_on = on.weight > 0

        if not is_on:
            matched = match(ft.name, on.matches, attrs)
            is_on = matched

        if is_on:
            matched = match(ft.name, off.matches, attrs)
            is_on = not matched
    elif ft.toggle_type == FeatureToggle.Type.PERCENTAGE:
        prcnt = ft.percentage
        if not prcnt or not prcnt.on or not prcnt.off or not prcnt.stickiness:
            raise FeatureToggleException(
                f' feature flag ${ft.name} is invalid')

        on_weight = prcnt.on.weight
        off_weight = prcnt.off.weight
        if (on_weight + off_weight != 100 or on_weight < 0 or off_weight < 0):
            raise FeatureToggleException(
                f'feature flag {ft.name} has invalid weights')

        stickiness = prcnt.stickiness
        if stickiness.stickiness_type == Stickiness.RANDOM:
            is_on = random() * 100 < on_weight
        elif stickiness.stickiness_type == Stickiness.KEYS:
            key_hash = hash(ft.name, stickiness.keys, prcnt.salt, attrs)
            is_on = key_hash % 1000000 < on_weight * 10000

        if not is_on:
            matched = match(ft.name, prcnt.on.matches, attrs)
            is_on = matched

        if is_on:
            matched = match(ft.name, prcnt.off.matches, attrs)
            is_on = not matched

    return is_on


def match(name: str, matches: Sequence[Match], attrs: Optional[Attrs]) -> bool:
    for match in matches:
        if not match.key or not match.key.key:
            raise FeatureToggleException(f'invalid match key for {name}')

        key = match.key.key
        attr = attrs.get(key) if attrs else None
        if attr is None:
            continue

        if match.key.key_type == Key.Type.BOOLEAN:
            if not isinstance(attr, bool):
                raise FeatureToggleException(
                    f'value passed for {key} is not boolean for feature flg {name}'
                )

            if not match.bool_op:
                raise FeatureToggleException(
                    f'no boolean operation set for {key} and feature flag {name}'
                )

            if match.bool_op.value:
                return True

        elif match.key.key_type == Key.DATE_TIME:
            if not isinstance(attr, datetime):
                raise FeatureToggleException(
                    f'value passed for {key} and feature flag {name} is not of type datetime'
                )
            date_op = match.date_time_op
            if not date_op or not date_op.timestamp:
                raise FeatureToggleException(
                    f'expected a DateTime op for {key} and feature flag {name}'
                )

            dt = match.date_time_op.timestamp.ToDatetime()
            if date_op.op == date_op.AFTER:
                return attr.timestamp() > dt.timestamp()
            elif date_op.op == date_op.BEFORE:
                return attr.timestamp() < dt.timestamp()

        elif match.key.key_type == Key.FLOAT:
            if not isinstance(attr, float) and not isinstance(attr, int):
                raise FeatureToggleException(
                    f'expected a float/int for attribute {key} and feature flag {name}'
                )
            if not match.float_op:
                raise FeatureToggleException(
                    f'expected a float op for attribute {key} and feature flag {name}'
                )

            op = match.float_op
            if len(op.values) < 1:
                raise FeatureToggleException(
                    f'expected values set for attribute {key} and feature flag {name}'
                )

            if op.op == op.IN:
                for val in op.values:
                    if val == attr:
                        return True
                return False

            if len(op.values) != 1:
                raise FeatureToggleException(
                    f'expected a single value for attribute {key} and feature flag {name}'
                )

            val = op.values[0]
            if op.op == op.EQ:
                return attr == val
            if op.op == op.GT:
                return attr > val
            if op.op == op.GTE:
                return attr >= val
            if op.op == op.LT:
                return attr < val
            if op.op == op.LTE:
                return attr <= val
            if op.op == op.NEQ:
                return attr != val

        elif match.key.key_type == Key.INT:
            if not isinstance(attr, float) and not isinstance(attr, int):
                raise FeatureToggleException(
                    f'expected a float/int for attribute {key} and feature flag {name}'
                )
            if not match.int_op:
                raise FeatureToggleException(
                    f'expected a integer op for attribute {key} and feature flag {name}'
                )

            op = match.int_op
            if len(op.values) < 1:
                raise FeatureToggleException(
                    f'expected values set for attribute {key} and feature flag {name}'
                )

            if op.op == op.IN:
                for val in op.values:
                    if val == attr:
                        return True
                return False

            if len(op.values) != 1:
                raise FeatureToggleException(
                    f'expected a single value for attribute {key} and feature flag {name}'
                )

            val = op.values[0]
            if op.op == op.EQ:
                return attr == val
            if op.op == op.GT:
                return attr > val
            if op.op == op.GTE:
                return attr >= val
            if op.op == op.LT:
                return attr < val
            if op.op == op.LTE:
                return attr <= val
            if op.op == op.NEQ:
                return attr != val

        elif match.key.key_type == Key.STRING:
            if not isinstance(attr, str):
                raise FeatureToggleException(
                    f'expected a str for attribute {key} and feature flag {name}'
                )
            if not match.string_op:
                raise FeatureToggleException(
                    f'expected a string op for attribute {key} and feature flag {name}'
                )

            op = match.string_op
            if len(op.values) < 1:
                raise FeatureToggleException(
                    f'expected values set for attribute {key} and feature flag {name}'
                )

            if op.op == op.IN:
                for val in op.values:
                    if val == attr:
                        return True
                return False

            if len(op.values) != 1:
                raise FeatureToggleException(
                    f'expected a single value for attribute {key} and feature flag {name}'
                )

            val = op.values[0]
            if op.op == op.EQ:
                return attr == val
            if op.op == op.CONTAINS:
                return attr.find(val) >= 0

    # Anything else unsupported. Fail silently with False.

    return False


def hash(name: str, keys: Sequence[Key], salt: str,
         attrs: Optional[Attrs]) -> int:
    if not attrs:
        raise FeatureToggleException(
            f'no attribute passed for feature flag {name}')

    if not keys:
        raise FeatureToggleException(
            f'no attributes defined for feature flag {name}')

    for key in keys:
        if not key.key:
            raise FeatureToggleException(
                f'empty attribute {key} for feature flag {name}')

        attr = attrs.get(key.key)
        if not attr:
            continue

        v = salt
        if key.key_type == Key.BOOLEAN:
            if not isinstance(attr, bool):
                raise FeatureToggleException(
                    f'expected boolean value for attribute {key.key} and feature flag {name}'
                )

            v += 'true' if attr else 'false'

        elif key.key_type == Key.STRING:
            if not isinstance(attr, str):
                raise FeatureToggleException(
                    f'expected str value for attribute {key.key} and feature flag {name}'
                )

            v += attr

        elif key.key_type == Key.FLOAT or key.key_type == Key.INT:
            if not isinstance(attr, float) and not isinstance(attr, int):
                raise FeatureToggleException(
                    f'expected float/int value for attribute {key.key} and feature flag {name}'
                )

            v += str(attr)

        elif key.key_type == Key.DATE_TIME:
            if not isinstance(attr, datetime):
                raise FeatureToggleException(
                    f'expected datetime value for attribute {key.key} and feature flag {name}'
                )

            v += str(int(1000 * attr.timestamp()))
        else:
            raise FeatureToggleException(
                f'unknown attribute type for attribute {key.key} and feature flag {name}'
            )

        return xxh64_intdigest(v)

    raise FeatureToggleException(f'no matching attribute for {name}')
