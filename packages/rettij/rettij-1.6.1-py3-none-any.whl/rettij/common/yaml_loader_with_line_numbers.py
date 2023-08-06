from typing import Dict, Any
from yaml import SafeLoader, MappingNode


# https://stackoverflow.com/questions/13319067/parsing-yaml-return-with-line-number
class YamlLoaderWithLineNumbers(SafeLoader):
    """
    This SafeLoader-based class also parses the line number of the current node.

    It does so by looking at the start mark of the currently parsed node. It then increases this value by one
    (since the line counter starts at 0) and adds it to the node's dictionary under the key '__line__'.
    """

    def construct_mapping(self, node: MappingNode, deep: bool = False) -> Dict[str, Any]:
        """
        Construct the mappings with file line numbers included.

        Overrides 'yaml.constructor.SafeConstructor.construct_mapping()'.

        :param node: MappingNode object.
        :param deep: Deep flag.
        :return: Dictionary containing the mapping.
        """
        mapping: Dict[str, Any] = super(YamlLoaderWithLineNumbers, self).construct_mapping(node, deep=deep)
        # Add 1 so line numbering starts at 1
        mapping["__line__"] = node.start_mark.line + 1
        return mapping
