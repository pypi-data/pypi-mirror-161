import toml


def instance_of(_type):
    def checker(val):
        return isinstance(val, _type)

    return checker


def get_config(global_config, override_config, key, check_fn):
    val = override_config.get(key, global_config.get(key, None))

    return val, val is not None, check_fn(val)


class Config:
    def __init__(self, global_config, override_config):
        for entry in self.schema:
            value, found, valid = get_config(
                global_config, override_config, entry["key"], entry["check_fn"]
            )

            if not found:
                self.__setattr__(entry["key"], entry["default"])
                continue

            if not valid:
                raise Exception(
                    f"In {self.__class__.__name__}, value of {entry['key']} is invalid."
                )

            self.__setattr__(entry["key"], value)


class OpConfiguration(Config):
    schema = [
        {"key": "dir", "check_fn": instance_of(str), "default": "*"},
        {"key": "add_docstrings", "check_fn": instance_of(bool), "default": True},
        {"key": "add_descriptions", "check_fn": instance_of(bool), "default": True},
        {"key": "add_no_data_dep_in", "check_fn": instance_of(bool), "default": True},
        {
            "key": "no_data_dep_name",
            "check_fn": instance_of(str),
            "default": "run_config",
        },
        {"key": "add_is_required", "check_fn": instance_of(bool), "default": True},
    ]


class ResourceConfiguration(Config):
    schema = [
        {"key": "add_docstrings", "check_fn": instance_of(bool), "default": True},
        {"key": "add_descriptions", "check_fn": instance_of(bool), "default": True},
        {"key": "add_is_required", "check_fn": instance_of(bool), "default": True},
    ]


class Configuration:
    def __init__(self, global_config, op_config, resources_config):
        self.ops = OpConfiguration(global_config, op_config)
        self.resources = ResourceConfiguration(global_config, resources_config)

    @classmethod
    def from_pyproject(cls):
        with open("./pyproject.toml", "r", encoding="utf8") as file:
            contents = toml.load(file)

        if "dagster_fmt" not in contents.get("tool", {}):
            return cls({}, {}, {})

        keys = ["ops", "resources"]
        output = [contents["tool"]["dagster_fmt"].get(key, {}) for key in keys]

        return cls(
            {k: v for k, v in contents["tool"]["dagster_fmt"].items() if k not in keys},
            *output,
        )
