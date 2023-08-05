import functools
import inspect
from collections import defaultdict
from types import MethodType
from typing import List, Dict, Callable, Tuple
from unittest.mock import MagicMock
from curia.api.swagger_client import PlatformApi
import curia.api.swagger_client.models as models_package
import re
from pymaybe import maybe
import uuid
from inspect import getframeinfo, stack

# pylint: disable=W0622,W0613
from curia.utils.string import to_snake_case, to_camel_case


def debug(message):
    caller = getframeinfo(stack()[1][0])
    print(f"[MockApi DEBUG: {caller.filename}:{caller.lineno}]: {message}")


class _MockApiInstanceBase:
    def __init__(self):
        seed_data, method_overrides = MockApiConfiguration.get_configuration()
        self.db = defaultdict(dict)
        self._load_seed_data(seed_data)
        self.method_overrides = method_overrides

    def _load_seed_data(self, seed_data):
        """
        Loads a list of seed models into the database

        :param seed_data: List of API models to load
        """
        for model in seed_data:
            self._load_model(model)

    def _load_model(self, model):
        self.db[type(model)][model.id] = model
        model_snake_case = to_snake_case(type(model).__name__)
        for key in model.attribute_map.keys():
            value = getattr(model, key)

            if type(value) in MODEL_MAP.values() and f"{key}_id" in model.attribute_map and "id" in value.attribute_map:
                # joined model case
                setattr(model, f"{key}_id", value.id)
                if model_snake_case in value.attribute_map:
                    setattr(value, model_snake_case, model)
                elif f"{model_snake_case}s" in value.attribute_map:
                    if isinstance(getattr(value, f"{model_snake_case}s"), list):
                        getattr(value, f"{model_snake_case}s").append(model)
                    else:
                        setattr(value, f"{model_snake_case}s", [model])
                self._load_model(value)
            if isinstance(value, list) and len(value) > 0 and f"{model_snake_case}_id" in value[0].attribute_map:
                # joined model case
                for joined_model in value:
                    setattr(joined_model, f"{model_snake_case}_id", model.id)

    def __getattribute__(self, name):
        try:
            method_overrides = object.__getattribute__(self, "method_overrides")
        except AttributeError:
            # handle case where object is still not fully initialized
            method_overrides = {}
        if name in method_overrides:
            return MethodType(method_overrides[name], self)
        return object.__getattribute__(self, name)

    def resolve_joins(self, models, joins: List[str]):
        assert len(models) > 0, "At least one model must be provided"
        for join in joins:
            current_models = models
            current_model_type = type(current_models[0])
            segmentation = join.split(".")
            for segment in segmentation:
                inverted_attribute_map = {value: key for key, value in current_model_type.attribute_map.items()}
                if segment not in inverted_attribute_map:
                    raise AttributeError(f"Cannot resolve join: {join}, {current_model_type} does not have an "
                                         f"attribute corresponding to {segment}")
                attribute_name = inverted_attribute_map[segment]
                attribute_swagger_type: str = current_model_type.swagger_types[attribute_name]
                if attribute_swagger_type.startswith("list["):
                    attribute_swagger_type = attribute_swagger_type[len("list["):-1]
                    next_model_type = MODEL_MAP[attribute_swagger_type]
                    current_model_type_snake_case = to_snake_case(current_model_type.__name__)
                    if f"{current_model_type_snake_case}_id" not in next_model_type.attribute_map:
                        raise Exception(f"Cannot resolve join: {join}, could not resolve relationship between "
                                        f"{current_model_type} and type {next_model_type}. It's possible that this is a "
                                        f"many to many relationship, which is not yet supported by this mocking "
                                        f"framework, or it is possible that the relationship does not exist. In order "
                                        f"to resolve the relationship, {next_model_type} must have the attribute "
                                        f"{current_model_type_snake_case}_id so that the reverse relationship can be "
                                        f"established.")
                    next_models = []
                    for individual_model in current_models:
                        associated_models = [
                            value for value in self.db[next_model_type].values()
                            if getattr(value, f"{current_model_type_snake_case}_id") == individual_model.id
                        ]
                        setattr(individual_model, attribute_name, associated_models)
                        next_models.extend(associated_models)
                else:
                    next_model_type = MODEL_MAP[attribute_swagger_type]
                    next_models = []
                    for individual_model in current_models:
                        next_model_id = getattr(individual_model, f"{attribute_name}_id")
                        if next_model_id is None:
                            raise Exception(f"{segment}_id value on {current_models} is null!")
                        # get next model and set attribute of current model
                        next_model = self.db[next_model_type][next_model_id]
                        setattr(individual_model, attribute_name, next_model)
                        next_models.append(next_model)
                current_models = next_models
                current_model_type = next_model_type


def configure_mock_api(seed_data: List[object], method_overrides: Dict[str, Callable]):
    mock_api_configuration = MockApiConfiguration(seed_data=seed_data, method_overrides=method_overrides)

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with mock_api_configuration:
                return fn(*args, **kwargs)

        return wrapper

    return decorator


class MockApiConfiguration:
    STACK: List['MockApiConfiguration'] = []

    def __init__(self, seed_data: List[object], method_overrides: Dict[str, Callable]):
        """
        Initialize and __enter__ a MockApiConfiguration to seed the mock API with certain values. MockApiConfiguration
        contexts stack -- e.g.:

        with MockApiConfiguration(..., ...):
            with MockApiConfiguration(..., ...):
                api_instance = MockApiInstance()

        Will have the api_instance configured with the seed data from both configurations and the methods from both
        configurations, with the innermost context having precedence.

        :param seed_data: List of API models to seed into the mock database
        :param method_overrides: Dict mapping strings (the names of methods) to callables that implement those methods.
            The callables should expect to receive self as the first argument
        """
        self.seed_data = seed_data
        self.method_overrides = method_overrides

    def __enter__(self):
        MockApiConfiguration.STACK.append(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        MockApiConfiguration.STACK.pop()

    @classmethod
    def get_configuration(cls) -> Tuple[List[object], Dict[str, Callable]]:
        """
        Retrieves the current seed data and method overrides to instantiate a mock API instance

        :return: seed_data as concatenated seed_datas from all configs in STACK, method_overrides as combined
            dictionary of all method_overrides in STACK, with innermost configs taking precedence
        """
        seed_data = []
        method_overrides = {}
        for configuration in cls.STACK:
            seed_data.extend(configuration.seed_data)
            method_overrides.update(configuration.method_overrides)
        return seed_data, method_overrides


def get_models():
    """
    Gets all model classes in autogenerated API by stepping through the package

    :return: List of all model classes in autogenerated API
    """
    return {
        model_name: getattr(models_package, model_name)
        for model_name in dir(models_package)
        if isinstance(getattr(models_package, model_name), type)
    }


MODEL_MAP = get_models()


def fn_get_one(models, model_type):
    """
    Constructs a method for getting a single object from the API mock database for an arbitrary model_type
    :param models: Dict mapping api model names to api model classes
    :param model_type: api model class, e.g. ProcessJob
    :return: Method that gets a single model from the API mock database
    """

    def get_one(self, id, **kwargs):
        if id in self.db[model_type]:
            if kwargs.get("join", None) is not None:
                self.resolve_joins([self.db[model_type][id]], kwargs["join"])
            return self.db[model_type][id]
        raise Exception("404 Model Not Found")

    return get_one


def fn_get_many(models, model_type):
    """
    Constructs a method for getting many objects from the API mock database for an arbitrary model_type
    See docs to implement more filter functionality:
    https://github.com/nestjsx/crud/wiki/Requests#filter

    :param models: Dict mapping api model names to api model classes
    :param model_type: api model class, e.g. ProcessJob
    :return: Method that gets several models from the API mock database
    """

    def get_many(self, **kwargs):
        to_return = []
        for model in self.db[model_type].values():
            if kwargs.get("filter", None) is not None:
                filter = kwargs["filter"]
                for f in filter:
                    field, condition, value = f.split("||")
                    field_snake_case = to_snake_case(field)
                    model_value = getattr(model, field_snake_case)
                    model_value_type = type(model_value)
                    # attempt to coerce type
                    try:
                        model_value = model_value_type(model_value)
                    except Exception as e:
                        debug(f"Failed to coerce type while processing filters; {e}. ")
                    valid = evaluate_condition(condition, model_value, value)
                    if not valid:
                        break
                else:
                    # for else: https://book.pythontips.com/en/latest/for_-_else.html
                    # only runs if there were no breaks (so no filters were invalid)
                    to_return.append(model)
        if "join" in kwargs:
            self.resolve_joins(to_return, kwargs["join"])
        return_type = models[f"GetMany{model_type.__name__}ResponseDto"]
        return return_type(data=to_return, count=len(to_return), total=len(to_return), page=0, page_count=1)

    return get_many


def evaluate_condition(condition, model_value, value):
    if condition == "$eq":
        valid = model_value == value
    elif condition == "$ne":
        valid = model_value != value
    elif condition == "$gt":
        valid = model_value > value
    elif condition == "$lt":
        valid = model_value < value
    elif condition == "$gte":
        valid = model_value >= value
    elif condition == "lte":
        valid = model_value <= value
    else:
        raise ValueError(f"Condition {condition} not recognized by the mock API. "
                         f"If you need it, implement it. (ask WK for reference as to how to do so)")
    return valid


def fn_create_one(models, model_type):
    """
    Constructs a method for creating one object the API mock database for an arbitrary model_type

    :param models: Dict mapping api model names to api model classes
    :param model_type: api model class, e.g. ProcessJob
    :return: Method that creates a object in the API mock database
    """

    def create_one(self, body, **kwargs):
        body.id = str(uuid.uuid4())
        self.db[model_type][body.id] = body
        return body

    return create_one


def fn_create_many(models, model_type):
    """
    Constructs a method for creating many objects in the API mock database for an arbitrary model_type

    :param models: Dict mapping api model names to api model classes
    :param model_type: api model class, e.g. ProcessJob
    :return: Method that creates many objects in the API mock database
    """

    def create_many(self, body, **kwargs):
        for model in body.bulk:
            model.id = str(uuid.uuid4())
            self.db[model_type][model.id] = model
        return body

    return create_many


def fn_update_one(models, model_type):
    """
    Constructs a method for updating one object in the API mock database for an arbitrary model_type

    :param models: Dict mapping api model names to api model classes
    :param model_type: api model class, e.g. ProcessJob
    :return: Method that updates one object in the API mock database
    """

    def update_one(self, id, body, **kwargs):
        if id not in self.db[model_type]:
            raise Exception("404 Model Not Found")
        body.id = id
        self.db[model_type][id] = body
        return body

    return update_one


def fn_delete_one(models, model_type):
    """
    Constructs a method for deleting one object in the API mock database for an arbitrary model_type

    :param models: Dict mapping api model names to api model classes
    :param model_type: api model class, e.g. ProcessJob
    :return: Method that deletes one object in the API mock database
    """

    def delete_one(self, id, **kwargs):
        if id not in self.db[model_type]:
            raise Exception("404 Model Not Found")
        del self.db[model_type][id]

    return delete_one


def fn_replace_one(models, model_type):
    """
    Constructs a method for replacing one object in the API mock database for an arbitrary model_type

    :param models: Dict mapping api model names to api model classes
    :param model_type: api model class, e.g. ProcessJob
    :return: Method that replaces one object in the API mock database
    """

    def replace_one(self, body, **kwargs):
        self.db[model_type][body.id] = body
        return body

    return replace_one


def fn_start(models, model_type):
    """
    Constructs a method for "starting" one object in the API mock database for an arbitrary model_type. No code
    is actually executed when the object is started, the status is just changed.

    :param models: Dict mapping api model names to api model classes
    :param model_type: api model class, e.g. ProcessJob
    :return: Method that starts one object in the API mock database
    """

    def start(self, id, **kwargs):
        if id not in self.db[model_type]:
            raise Exception("404 Model Not Found")
        self.db[model_type][id].status = "RUNNING"
        return self.db[model_type][id]

    return start


def fn_stop(models, model_type):
    """
    Constructs a method for "stopping" one object in the API mock database for an arbitrary model_type. No code
    is actually executed when the object is stopped, the status is just changed.

    :param models: Dict mapping api model names to api model classes
    :param model_type: api model class, e.g. ProcessJob
    :return: Method that stops one object in the API mock database
    """

    def stop(self, id, **kwargs):
        if id not in self.db[model_type]:
            raise Exception("404 Model Not Found")
        self.db[model_type][id].status = "ABORTED"
        return self.db[model_type][id]

    return stop


def fn_status(models, model_type):
    """
    Constructs a method for getting the status of one object in the API mock database for an arbitrary model_type.

    :param models: Dict mapping api model names to api model classes
    :param model_type: api model class, e.g. ProcessJob
    :return: Method that gets the status of one object in the API mock database
    """

    def status(self, id, **kwargs):
        if id in self.db[model_type]:
            if id not in self.db[model_type]:
                raise Exception("404 Model Not Found")
            return self.db[model_type][id]
        raise Exception("404 Model Not Found")

    return status


def default_functionality_builder(method, models):
    """
    Tries to parse the return type of a method from its docstring and creates a method that returns a MagicMock
    of that return type

    :param method: Method to mock
    :param models: List of models
    :return: function that mocks the default functionality of a model
    """
    return_line = [line.strip() for line in maybe(method.__doc__).split("\n").or_else("") if ":return:" in line]
    return_type = maybe(return_line or None).split()[1].or_else(None)

    if return_type is not None and return_type in models:
        @functools.wraps(method)
        def function(self, *args, **kwargs):
            return MagicMock(models[return_type])
    else:
        if return_type is not None:
            debug(f"{return_type} of method {method} is not a model; reverting to default MagicMock")

        @functools.wraps(method)
        def function(self, *args, **kwargs):
            return MagicMock()
    return function


# matches model names to functionality builders
regex_to_functionality_builder = {
    r"get_one_base_([a-z_]*)_controller_\1": fn_get_one,
    r"get_many_base_([a-z_]*)_controller_\1": fn_get_many,
    r"create_one_base_([a-z_]*)_controller_\1": fn_create_one,
    r"create_many_base_([a-z_]*)_controller_\1": fn_create_many,
    r"update_one_base_([a-z_]*)_controller_\1": fn_update_one,
    r"delete_one_base_([a-z_]*)_controller_\1": fn_delete_one,
    r"replace_one_base_([a-z_]*)_controller_\1": fn_replace_one,
    r"([a-z_]*)_controller_start": fn_start,
    r"([a-z_]*)_controller_stop": fn_stop,
    r"([a-z_]*)_controller_status": fn_status,
}


def get_functionality(models, method_name, method):
    """
    Parses a method name and builds the appropriate functionality around it, e.g. methods that look like
    create_one_base_{}_controller_{} will actually create a {} in the mock database

    :param models: List of parsed models
    :param method_name: Name of method to implement
    :param method: Actual method to implement
    :return: boolean representing whether functionality was parsed and created, Method mocking functionality
    """
    for pattern, functionality_builder in regex_to_functionality_builder.items():
        compiled_pattern = re.compile(pattern)
        match = compiled_pattern.fullmatch(method_name)
        if match:
            model_type_snake_case = match.group(1)
            model_type_camel_case = to_camel_case(model_type_snake_case)
            if model_type_camel_case not in models:
                raise ValueError(f"Could not find model for method {method_name}! "
                                 f"(parsed snake case: {model_type_snake_case})"
                                 f"(parsed camel case: {model_type_camel_case})")
            return True, functionality_builder(models, models[model_type_camel_case])
    return False, default_functionality_builder(method, models)


def get_mock_api_instance_class():
    """
    Builds the mock api instance class by reading the actual api instance
    :return: MockApiInstance class
    """
    method_dict = {}
    debug(f"Found {len(MODEL_MAP.keys())} models")
    n_specialized = 0
    for method_name, method in inspect.getmembers(PlatformApi, predicate=inspect.isfunction):
        if method_name.startswith("__"):
            continue
        specialized, new_method_functionality = get_functionality(MODEL_MAP, method_name, method)
        method_dict[method_name] = new_method_functionality
        if specialized:
            n_specialized += 1

    debug(f"Found {len(method_dict.keys())} methods, {n_specialized} of which have autogenerated functionality.")

    return type("MockApiInstance", (_MockApiInstanceBase,), method_dict)


MockApiInstance = get_mock_api_instance_class()
