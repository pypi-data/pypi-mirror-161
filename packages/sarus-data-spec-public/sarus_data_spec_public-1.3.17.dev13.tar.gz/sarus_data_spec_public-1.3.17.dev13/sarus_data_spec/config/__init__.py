import os

import yaml

routing_file = os.path.join(os.path.dirname(__file__), "routing.yaml")
with open(routing_file) as f:
    ROUTING = yaml.load(f.read(), Loader=yaml.Loader)

properties_file = os.path.join(
    os.path.dirname(__file__), "privacy_properties.yaml"
)
with open(properties_file) as f:
    privacy_properties = yaml.load(f.read(), Loader=yaml.Loader)

WHITELISTED_TRANSFORMS = privacy_properties["WHITELISTED_TRANSFORMS"]

__all__ = ["ROUTING", "WHITELISTED_TRANSFORMS"]
