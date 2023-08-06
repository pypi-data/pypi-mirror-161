from validator import Validator
from jsonpath_ng import parse
import logging
from typing import List
from flask import request, abort
from functools import wraps

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ValidationError(Exception):
    """Wraps around request validation errors"""


class RequestFilter(object):
    def validate(self, data: dict, filter_groups: List[dict]) -> bool:
        """
        Returns True if atleast one filter group is validated or raises a
        validation exception if none of the filter groups are validated.

        Arguments:
            data: Dictionary of request
            filter_groups: List of filter groups containig JSON path keys to
                parse `data` with and Validator rules to validate with.
                JSON path syntax: https://goessner.net/articles/JsonPath/
                Validator rules syntax: https://github.com/CSenshi/Validator/blob/master/RULES.md
        """
        for group in filter_groups:
            log.debug(f"Filter group:\n{group}")
            results = {}
            for path, rule in group.items():
                try:
                    results[path] = [match.value for match in parse(path).find(data)][0]
                except IndexError:
                    request[path] = ""
            log.debug(f"Request mapping:\n{results}")

            val = Validator(results, group)
            is_valid = val.validate()

            log.debug(f"Validated data:\n{val.get_validated_data()}")
            errors = val.get_errors()
            log.debug(f"Validation errors: {errors}")

            if is_valid:
                return True

        raise ValidationError(errors)

    def request_filter_groups(self, filter_groups: List[dict], flask=False):
        """
        Decorator function that returns the passed function with original arguments
        if validation is successful or returns a validation error response.

        filter_groups: List of filter groups containig JSON path keys to
            parse `data` with and Validator rules to validate with.
            JSON path syntax: https://goessner.net/articles/JsonPath/
            Validator rules syntax: https://github.com/CSenshi/Validator/blob/master/RULES.md
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if flask:
                    data = request.json
                else:
                    data = args[0]
                try:
                    self.validate(data, filter_groups)
                except ValidationError as e:
                    log.error(e, exc_info=True)
                    if flask:
                        abort(422, e)
                    else:
                        return {"statusCode": 422, "body": e}

                return func(*args, **kwargs)

            return wrapper

        return decorator
