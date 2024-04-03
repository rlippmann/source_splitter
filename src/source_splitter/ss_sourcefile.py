"""Bass Class representation of a source file."""

import pathlib
from tree_sitter import Node
from tree_sitter_languages import get_parser
from .ss_exceptions import SSParseFailed
from .ss_items import (
    SSLanguageMappings,
    TS_IMPORT_NODE_TYPES,
    TS_INTERFACE_NODE_TYPES,
    TS_LITERAL_NODE_TYPES,
    TS_COMMENT_NODE_TYPES,
    TS_FUNCTION_NODE_TYPES,
    TS_CLASS_NODE_TYPES,
    TS_METHOD_NODE_TYPES,
)

DUMMY_LITERAL_FOR_TEST = "DUMMY_LITERAL"
DUMMY_LITERAL2_FOR_TEST = False
DUMMY_LITERAL3_FOR_TEST = 200


def dummy_function_for_test() -> None:
    """Dummy function for test."""

    def dummy_subfunction_for_test() -> None:
        """Dummy subfunction for test."""
        print("DUMMY_SUBFUNCTION")

    dummy_subfunction_for_test()


class SSSourceFile:
    """Bass Class representation of a source file."""

    def __init__(self, filename: pathlib.Path, language: str | None) -> None:
        """
        Initializes a new instance of the class.

        Parameters:
            filename (str): The name of the file.
            language (str | None): The language of the file.

        Attributes:
            filename (str): The name of the file.
            source_code (bytes): The content of the file as bytes.
            tree_cursor (TreeCursor | None): The TreeCursor of the file.

        Returns:
            None
        """
        self.filename = pathlib.Path(filename)
        self.source_code = self.filename.read_bytes()
        self.tree_root: Node | None = None
        self.language = language
        self.literals: list[Node] = []
        self.comments: list[Node] = []
        self.imports: list[Node] = []
        self.import_format = "import ./{filename}"
        self.import_directory_specifier = "/"
        self.import_suffix = ""
        if language:
            self.parse()

    def parse(self) -> None:
        """
        Creates the root node for the parse tree of the file

        Parameters:
            language (str): The language of the file.

        Returns:
            None

        Raises:
            ValueError: If the language is empty.
            ValueError: If the language extension doesn't match the language.
            ParseFailed: If the file cannot be parsed.
        """
        if not self.language:
            raise ValueError("Language cannot be empty.")
        if self.filename.suffix not in SSLanguageMappings[self.language][0]:
            if not (alternate_language := SSLanguageMappings[self.language][1]):
                raise ValueError(f"File {self.filename} is not a {self.language} file.")
            if self.filename.suffix not in SSLanguageMappings[alternate_language]:
                raise ValueError(f"File {self.filename} is not a {self.language} file.")

        parser = get_parser(self.language)
        self.tree_root = parser.parse(self.source_code).root_node
        if not self.tree_root:
            raise SSParseFailed(f"Failed to parse {self.filename}.")
        self.imports = self.get_nodes(TS_IMPORT_NODE_TYPES, self.tree_root, True)
        self.literals = self.get_nodes(TS_LITERAL_NODE_TYPES, self.tree_root, True)
        self.comments = self.get_nodes(TS_COMMENT_NODE_TYPES, self.tree_root, True)

    def check_tree_root(self) -> None:
        """
        Checks if the tree root is None.

        Raises:
            ValueError: If the tree root is None.

        Returns:
            None
        """
        if self.tree_root is None:
            raise ValueError(f"Source file {self.filename} has not been parsed.")

    @staticmethod
    def sort_nodes(nodes: list[Node]) -> None:
        """
        Sorts a list of nodes.

        Args:
            nodes (list[Node]): The list of nodes to sort.

        Returns:
            None
        """
        nodes.sort(key=lambda node: node.start_byte)

    def extract_nodes(
        self, child_nodes: list[Node], parent_nodes: list[Node]
    ) -> tuple[list[Node], list[Node]]:
        """
        Extracts nodes from a list of nodes.

        Args:
            child_nodes (list[Node]): The list of nodes to extract from.
            parent_nodes (list[Node]): Extract nodes who have these nodes as parents.
        Returns:
            tuple[list[Node], list[Node]]: A tuple of the extracted nodes.
                    The first list contains the extracted nodes.
                    The second list contains the remaining nodes.
        """
        return_nodes: list[Node] = []
        remaining_nodes: list[Node] = []
        parent_index = 0
        child_index = 0

        while parent_index < len(parent_nodes) and child_index < len(child_nodes):
            parent_element = parent_nodes[parent_index]
            child_element = child_nodes[child_index]

            if SSSourceFile.is_inside(child_element, parent_element):
                # Function is within the current class
                return_nodes.append(child_element)
                child_index += 1
            elif child_element.start_byte > parent_element.end_byte:
                # Move to the next class
                parent_index += 1
            else:
                # Function is not within the current class
                remaining_nodes.append(child_element)
                child_index += 1

        # If there are remaining functions after the last class
        remaining_nodes.extend(child_nodes[child_index:])
        return (return_nodes, remaining_nodes)

    def print_source(self, node: Node) -> str:
        """
        Prints the source code of a node.

        Args:
            node (Node): The node to print the source code of.

        Returns:
            str: The source code of the node.
        """
        return self.source_code[node.start_byte : node.end_byte].decode("utf-8")

    def get_node_name(self, node: Node) -> str | None:
        """
        Retrieves the name of a node.

        Args:
            node (Node): The node to retrieve the name of.

        Returns:
            str: The name of the node.
        """
        identifier_node = node.children[0] if node.children else None
        return identifier_node.text.decode("utf-8") if identifier_node else None

    def get_nodes(
        self, names: set[str], start_node: Node, first_occurrence: bool = True
    ) -> list[Node]:
        """
        Retrieves a list of nodes by name.

        Args:
            name (list[str]): The name of the nodes to retrieve.

        Returns:
            list[Node]: A list of nodes with the specified name.
        """
        node_list: list[Node] = []

        def _walk_tree(node: Node) -> None:
            if node.type in names:
                node_list.append(node)
                if first_occurrence:
                    return
            for child in node.children:
                _walk_tree(child)

        self.check_tree_root()
        assert self.tree_root is not None  # For mypy
        for node in start_node.children:
            _walk_tree(node)
        self.sort_nodes(node_list)
        return node_list

    @staticmethod
    def is_inside(inner_node: Node, outer_node: Node) -> bool:
        """
        Checks if an inner node is inside an outer node.

        Args:
            inner_node (Node): The inner node.
            outer_node (Node): The outer node.

        Returns:
            bool: True if the inner node is inside the outer node, False otherwise.
        """
        return (
            inner_node.start_byte >= outer_node.start_byte
            and inner_node.end_byte <= outer_node.end_byte
        )


class SSFunctionLanguageSourceFile(SSSourceFile):
    """
    Class for managing source code languages with functions.
    """

    def __init__(self, filename: pathlib.Path, language: str | None) -> None:
        """
        Initializes a new instance of the class.

        Args:
            source_code (bytes): The source code of the file.
            filename (str): The name of the file.

        Returns:
            None
        """
        self.functions: list[Node] = []
        self.subfunctions: list[Node] = []
        super().__init__(filename, language)

    def parse(self) -> None:
        """
        Parse the source code of the file.

        Args:
            language (str): The language of the file.

        Returns:
            None
        """
        if self.functions or self.subfunctions:
            return
        super().parse()
        self.check_tree_root()
        assert self.tree_root is not None  # for mypy
        self.functions = self.get_nodes(TS_FUNCTION_NODE_TYPES, self.tree_root)
        for func in self.functions:
            self.subfunctions += self.get_nodes(TS_FUNCTION_NODE_TYPES, func)
        _, self.literals = self.extract_nodes(self.literals, self.functions)


class SSClassLanguageSourceFile(SSFunctionLanguageSourceFile):
    """Class for managing source code languages with classes."""

    def __init__(self, filename: pathlib.Path, language: str | None) -> None:
        """Initialize a new instance of the class.

        Args:
            filename (str): The name of the file.
            language (str | None): The language of the file.
        """
        self.classes: list[Node] = []
        self.methods: list[Node] = []
        super().__init__(filename, language)

    def parse(self) -> None:
        """
        Parse the source code of the file.

        Returns:
            None
        """
        if self.methods or self.classes:
            return
        super().parse()
        self.check_tree_root()
        assert self.tree_root is not None  # for mypy
        self.classes = self.get_nodes(TS_CLASS_NODE_TYPES, self.tree_root)
        # see if we have a method definition node type
        self.methods = self.get_nodes(TS_METHOD_NODE_TYPES, self.tree_root)
        if not self.methods:
            (self.methods, self.functions) = self.extract_nodes(
                self.functions, self.classes
            )
        _, self.literals = self.extract_nodes(self.literals, self.classes)


class SSInterfaceLanguageSourceFile(SSClassLanguageSourceFile):
    """Class for managing source code languages with interfaces."""

    def __init__(self, filename: pathlib.Path, language: str | None) -> None:
        """Initialize a new instance of the class.

        Args:
            filename (str): The name of the file.
            language (str | None): The language of the file.
        """
        self.interfaces: list[Node] = []
        super().__init__(filename, language)

    def parse(self) -> None:
        """
        Parse the source code of the file.

        Returns:
            None
        """
        if self.interfaces:
            return
        super().parse()
        self.check_tree_root()
        assert self.tree_root is not None  # for mypy
        self.interfaces = self.get_nodes(TS_INTERFACE_NODE_TYPES, self.tree_root)
