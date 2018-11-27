import re

from jsonschema import _utils
from jsonschema.exceptions import FormatError, ValidationError
from jsonschema.compat import iteritems


def patternProperties(validator, patternProperties, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for pattern, subschema in iteritems(patternProperties):
        for k, v in iteritems(instance):
            if re.search(pattern, k):
                for error in validator.descend(
                    v, subschema, path=k, schema_path=pattern,
                ):
                    yield error


def propertyNames(validator, propertyNames, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for property in instance:
        for error in validator.descend(
            instance=property,
            schema=propertyNames,
            path=property,  # FIXME: path?
        ):
            yield error


def additionalProperties(validator, aP, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    extras = set(_utils.find_additional_properties(instance, schema))

    if validator.is_type(aP, "object"):
        for extra in extras:
            for error in validator.descend(instance[extra], aP, path=extra):
                yield error
    elif not aP and extras:
        if "patternProperties" in schema:
            patterns = sorted(schema["patternProperties"])
            if len(extras) == 1:
                verb = "does"
            else:
                verb = "do"
            error = "tag-msg_requestParmValueCheck_regex. tagPara :%s %s, not match any of the regexes: %s" % (
                ", ".join(map(repr, sorted(extras))),
                verb,
                ", ".join(map(repr, patterns)),
            )
            yield ValidationError(error)
        else:
            error = "tag-msg_requestParmCheck_additional. Additional properties are not allowed (tagPara :%s %s, unexpected)"
            yield ValidationError(error % _utils.extras_msg(extras))


def items_draft3_draft4(validator, items, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    if validator.is_type(items, "object"):
        for index, item in enumerate(instance):
            for error in validator.descend(item, items, path=index):
                yield error
    else:
        for (index, item), subschema in zip(enumerate(instance), items):
            for error in validator.descend(
                item, subschema, path=index, schema_path=index,
            ):
                yield error


def items(validator, items, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    if items is True:
        items = {}
    elif items is False:
        items = {"not": {}}

    if validator.is_type(items, "object"):
        for index, item in enumerate(instance):
            for error in validator.descend(item, items, path=index):
                yield error
    else:
        for (index, item), subschema in zip(enumerate(instance), items):
            for error in validator.descend(
                item, subschema, path=index, schema_path=index,
            ):
                yield error


def additionalItems(validator, aI, instance, schema):
    if (
        not validator.is_type(instance, "array") or
        validator.is_type(schema.get("items", {}), "object")
    ):
        return

    len_items = len(schema.get("items", []))
    if validator.is_type(aI, "object"):
        for index, item in enumerate(instance[len_items:], start=len_items):
            for error in validator.descend(item, aI, path=index):
                yield error
    elif not aI and len(instance) > len(schema.get("items", [])):
        error = "tag-msg_requestParmCheck_additional.Additional items are not allowed (tagPara :%s %s, unexpected)"
        yield ValidationError(
            error %
            _utils.extras_msg(instance[len(schema.get("items", [])):])
        )


def const(validator, const, instance, schema):
    if instance != const:
        yield ValidationError("tag-msg_requestParmValueCheck_schema.tagPara :%r, was expected" % (const,))


def contains(validator, contains, instance, schema):
    if not validator.is_type(instance, "array"):
        return

    if not any(validator.is_valid(element, contains) for element in instance):
        yield ValidationError(
            "tag-msg_requestParmValueCheck_schema. tagPara :%r, are not valid under the given schema" % (instance,)
        )


def minimum_draft3_draft4(validator, minimum, instance, schema):
    if not validator.is_type(instance, "number"):
        return

    if schema.get("exclusiveMinimum", False):
        failed = instance <= minimum
        cmp = "less than or equal to"
    else:
        failed = instance < minimum
        cmp = "less than"

    if failed:
        yield ValidationError(
            "tag-msg_requestParmValueCheck_countMin.tagPara :%r, is %s the minimum of %r" % (instance, cmp, minimum)
        )


def maximum_draft3_draft4(validator, maximum, instance, schema):
    if not validator.is_type(instance, "number"):
        return

    if schema.get("exclusiveMaximum", False):
        failed = instance >= maximum
        cmp = "greater than or equal to"
    else:
        failed = instance > maximum
        cmp = "greater than"

    if failed:
        yield ValidationError(
            "tag-msg_requestParmValueCheck_countMax.tagPara :%r, is %s the maximum of %r" % (instance, cmp, maximum)
        )


def exclusiveMinimum_draft6(validator, minimum, instance, schema):
    if not validator.is_type(instance, "number"):
        return

    if instance <= minimum:
        yield ValidationError(
            "tag-msg_requestParmValueCheck_countMin.tagPara :%r, is less than or equal to the minimum of %r" % (
                instance, minimum,
            ),
        )


def exclusiveMaximum_draft6(validator, maximum, instance, schema):
    if not validator.is_type(instance, "number"):
        return

    if instance >= maximum:
        yield ValidationError(
            "tag-msg_requestParmValueCheck_countMax.tagPara :%r, is greater than or equal to the maximum of %r" % (
                instance, maximum,
            ),
        )


def minimum(validator, minimum, instance, schema):
    if not validator.is_type(instance, "number"):
        return

    if instance < minimum:
        yield ValidationError(
            "tag-msg_requestParmValueCheck_countMin.tagPara :%r, is less than the minimum of %r" % (instance, minimum)
        )


def maximum(validator, maximum, instance, schema):
    if not validator.is_type(instance, "number"):
        return

    if instance > maximum:
        yield ValidationError(
            "tag-msg_requestParmValueCheck_countMax.tagPara :%r, is greater than the maximum of %r" % (instance, maximum)
        )


def multipleOf(validator, dB, instance, schema):
    if not validator.is_type(instance, "number"):
        return

    if isinstance(dB, float):
        quotient = instance / dB
        failed = int(quotient) != quotient
    else:
        failed = instance % dB

    if failed:
        yield ValidationError("%r is not a multiple of %r" % (instance, dB))


def minItems(validator, mI, instance, schema):
    if validator.is_type(instance, "array") and len(instance) < mI:
        yield ValidationError("tag-msg_requestParmValueCheck_sizeMin.tagPara :%r, is too short" % (instance,))


def maxItems(validator, mI, instance, schema):
    if validator.is_type(instance, "array") and len(instance) > mI:
        yield ValidationError("tag-msg_requestParmValueCheck_sizeMax.tagPara :%r, is too long" % (instance,))


def uniqueItems(validator, uI, instance, schema):
    if (
        uI and
        validator.is_type(instance, "array") and
        not _utils.uniq(instance)
    ):
        yield ValidationError("tag-msg_requestParmCheck_duplicate.tagPara :%r, has non-unique elements" % (instance,))


def pattern(validator, patrn, instance, schema):
    if (
        validator.is_type(instance, "string") and
        not re.search(patrn, instance)
    ):
        yield ValidationError("tag-msg_requestParmValueCheck_regex.tagPara :%r, does not match %r" % (instance, patrn))


def format(validator, format, instance, schema):
    if validator.format_checker is not None:
        try:
            validator.format_checker.check(instance, format)
        except FormatError as error:
            yield ValidationError(error.message, cause=error.cause)


def minLength(validator, mL, instance, schema):
    if validator.is_type(instance, "string") and len(instance) < mL:
        yield ValidationError("tag-msg_requestParmValueCheck_sizeMin.tagPara :%r, is too short" % (instance,))


def maxLength(validator, mL, instance, schema):
    if validator.is_type(instance, "string") and len(instance) > mL:
        yield ValidationError("tag-msg_requestParmValueCheck_sizeMax.tagPara :%r, is too long" % (instance,))


def dependencies(validator, dependencies, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for property, dependency in iteritems(dependencies):
        if property not in instance:
            continue

        if dependency is True:
            dependency = {}
        elif dependency is False:
            dependency = {"not": {}}

        if validator.is_type(dependency, "object"):
            for error in validator.descend(
                instance, dependency, schema_path=property,
            ):
                yield error
        else:
            dependencies = _utils.ensure_list(dependency)
            for dependency in dependencies:
                if dependency not in instance:
                    yield ValidationError(
                        "%r is a dependency of %r" % (dependency, property)
                    )


def enum(validator, enums, instance, schema):
    if instance not in enums:
        yield ValidationError("tag-msg_requestParmValueCheck_block.tagPara :%r, is not one of %r" % (instance, enums))


def ref(validator, ref, instance, schema):
    resolve = getattr(validator.resolver, "resolve", None)
    if resolve is None:
        with validator.resolver.resolving(ref) as resolved:
            for error in validator.descend(instance, resolved):
                yield error
    else:
        scope, resolved = validator.resolver.resolve(ref)
        validator.resolver.push_scope(scope)

        try:
            for error in validator.descend(instance, resolved):
                yield error
        finally:
            validator.resolver.pop_scope()


def type_draft3(validator, types, instance, schema):
    types = _utils.ensure_list(types)

    all_errors = []
    for index, type in enumerate(types):
        if validator.is_type(type, "object"):
            errors = list(validator.descend(instance, type, schema_path=index))
            if not errors:
                return
            all_errors.extend(errors)
        else:
            if validator.is_type(instance, type):
                return
    else:
        yield ValidationError(
            _utils.types_msg(instance, types), context=all_errors,
        )


def properties_draft3(validator, properties, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for property, subschema in iteritems(properties):
        if property in instance:
            for error in validator.descend(
                instance[property],
                subschema,
                path=property,
                schema_path=property,
            ):
                yield error
        elif subschema.get("required", False):
            error = ValidationError("tag-msg_requestParmCheck_missReq.tagPara :%r, is a required property" % property)
            error._set(
                validator="required",
                validator_value=subschema["required"],
                instance=instance,
                schema=schema,
            )
            error.path.appendleft(property)
            error.schema_path.extend([property, "required"])
            yield error


def disallow_draft3(validator, disallow, instance, schema):
    for disallowed in _utils.ensure_list(disallow):
        if validator.is_valid(instance, {"type": [disallowed]}):
            yield ValidationError(
                "tag-msg_requestParmValueCheck_block.%r is disallowed for tagPara :%r," % (disallowed, instance)
            )


def extends_draft3(validator, extends, instance, schema):
    if validator.is_type(extends, "object"):
        for error in validator.descend(instance, extends):
            yield error
        return
    for index, subschema in enumerate(extends):
        for error in validator.descend(instance, subschema, schema_path=index):
            yield error


def type(validator, types, instance, schema):
    types = _utils.ensure_list(types)

    if not any(validator.is_type(instance, type) for type in types):
        yield ValidationError(_utils.types_msg(instance, types))


def properties(validator, properties, instance, schema):
    if not validator.is_type(instance, "object"):
        return

    for property, subschema in iteritems(properties):
        if property in instance:
            for error in validator.descend(
                instance[property],
                subschema,
                path=property,
                schema_path=property,
            ):
                yield error


def required(validator, required, instance, schema):
    if not validator.is_type(instance, "object"):
        return
    for property in required:
        if property not in instance:
            yield ValidationError("tag-msg_requestParmCheck_missGroup.tagPara :%r, is a required property" % property)


def minProperties(validator, mP, instance, schema):
    if validator.is_type(instance, "object") and len(instance) < mP:
        yield ValidationError(
            "tag-msg_requestParmCheck_missReq.tagPara :%r, does not have enough properties" % (instance,)
        )


def maxProperties(validator, mP, instance, schema):
    if not validator.is_type(instance, "object"):
        return
    if validator.is_type(instance, "object") and len(instance) > mP:
        yield ValidationError("tag-msg_requestParmCheck_invalid.tagPara :%r, has too many properties" % (instance,))


def allOf_draft4(validator, allOf, instance, schema):
    for index, subschema in enumerate(allOf):
        for error in validator.descend(instance, subschema, schema_path=index):
            yield error


def allOf(validator, allOf, instance, schema):
    for index, subschema in enumerate(allOf):
        if subschema is True:  # FIXME: Messages
            subschema = {}
        elif subschema is False:
            subschema = {"not": {}}
        for error in validator.descend(instance, subschema, schema_path=index):
            yield error


def oneOf_draft4(validator, oneOf, instance, schema):
    subschemas = enumerate(oneOf)
    all_errors = []
    for index, subschema in subschemas:
        errs = list(validator.descend(instance, subschema, schema_path=index))
        if not errs:
            first_valid = subschema
            break
        all_errors.extend(errs)
    else:
        yield ValidationError(
            "tag-msg_requestParmCheck_invalid.tagPara :%r, is not valid under any of the given schemas" % (instance,),
            context=all_errors,
        )

    more_valid = [s for i, s in subschemas if validator.is_valid(instance, s)]
    if more_valid:
        more_valid.append(first_valid)
        reprs = ", ".join(repr(schema) for schema in more_valid)
        yield ValidationError(
            "tag-msg_requestParmCheck_invalid.tagPara :%r, is valid under each of %s" % (instance, reprs)
        )


def anyOf_draft4(validator, anyOf, instance, schema):
    all_errors = []
    for index, subschema in enumerate(anyOf):
        errs = list(validator.descend(instance, subschema, schema_path=index))
        if not errs:
            break
        all_errors.extend(errs)
    else:
        yield ValidationError(
            "tag-msg_requestParmValueCheck_schema.tagPara :%r, is not valid under any of the given schemas" % (instance,),
            context=all_errors,
        )


def anyOf(validator, anyOf, instance, schema):
    all_errors = []
    for index, subschema in enumerate(anyOf):
        if subschema is True:  # FIXME: Messages
            subschema = {}
        elif subschema is False:
            subschema = {"not": {}}
        errs = list(validator.descend(instance, subschema, schema_path=index))
        if not errs:
            break
        all_errors.extend(errs)
    else:
        yield ValidationError(
            "tag-msg_requestParmValueCheck_schema.tagPara :%r, is not valid under any of the given schemas" % (instance,),
            context=all_errors,
        )


def oneOf(validator, oneOf, instance, schema):
    subschemas = enumerate(oneOf)
    all_errors = []
    for index, subschema in subschemas:
        if subschema is True:  # FIXME: Messages
            subschema = {}
        elif subschema is False:
            subschema = {"not": {}}
        errs = list(validator.descend(instance, subschema, schema_path=index))
        if not errs:
            first_valid = subschema
            break
        all_errors.extend(errs)
    else:
        yield ValidationError(
            "tag-msg_requestParmValueCheck_schema.tagPara :%r, is not valid under any of the given schemas" % (instance,),
            context=all_errors,
        )

    more_valid = [s for i, s in subschemas if validator.is_valid(instance, s)]
    if more_valid:
        more_valid.append(first_valid)
        reprs = ", ".join(repr(schema) for schema in more_valid)
        yield ValidationError(
            "tag-msg_requestParmValueCheck_schema.tagPara :%r, is valid under each of %s" % (instance, reprs)
        )


def not_(validator, not_schema, instance, schema):
    if validator.is_valid(instance, not_schema):
        yield ValidationError(
            "tag-msg_requestParmValueCheck_block.%r is not allowed for tagPara :%r," % (not_schema, instance)
        )