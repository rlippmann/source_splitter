"""Source splitter language specific source code items."""

import pathlib
from tree_sitter import Node
from .ss_exceptions import SSNoLanguageFound, SSParseFailed
from .ss_sourcefile import (
    SSClassLanguageSourceFile,
    SSInterfaceLanguageSourceFile,
    SSFunctionLanguageSourceFile,
)
from .ss_items import (
    SSLanguageMappings,
    SSLANGUAGE_C,
    SSLANGUAGE_CPP,
    SSLANGUAGE_JAVA,
    SSLANGUAGE_JS,
    SSLANGUAGE_PYTHON,
    SSLANGUAGE_TS,
)


class SSPythonSourceFile(SSClassLanguageSourceFile):
    """Source splitter language specific source code items."""

    def __init__(self, filename: pathlib.Path) -> None:
        """Initialize a new instance of the class.

        Args:
            filename (str): The name of the file.
        """
        super().__init__(filename, SSLANGUAGE_PYTHON)
        self.import_format = "import .%s"
        self.import_directory_specifier = "."
        self._extract_comments()

    def _extract_comments(self) -> None:
        """Extract comments from the source code.

        Returns:
            None
        """
        self.check_tree_root()
        assert self.tree_root is not None  # for mypy
        stmt_strs: list[Node] = self.get_nodes({"string"}, self.tree_root, True)
        for stmt in stmt_strs:
            if stmt.parent and stmt.parent.type == "expression_statement":
                self.comments.append(stmt)


class SSJavaSourceFile(SSInterfaceLanguageSourceFile):
    """Source splitter language JavaScript specific source code items."""

    def __init__(self, filename: pathlib.Path) -> None:
        """Initialize a new instance of the class.

        Args:
            filename (str): The name of the file.
        """
        super().__init__(filename, SSLANGUAGE_JAVA)


class SSJavaScriptSourceFile(SSClassLanguageSourceFile):
    """Source splitter language JavaScript specific source code items."""

    def __init__(self, filename: pathlib.Path) -> None:
        """Initialize a new instance of the class.

        Args:
            filename (str): The name of the file.
        """
        super().__init__(filename, SSLANGUAGE_JS)


class SSTypeScriptSourceFile(SSInterfaceLanguageSourceFile):
    """Source splitter language TypeScript specific source code items."""

    def __init__(self, filename: pathlib.Path) -> None:
        """Initialize a new instance of the class.

        Args:
            filename (str): The name of the file.
        """
        super().__init__(filename, SSLANGUAGE_TS)


class SSCppSourceFile(SSClassLanguageSourceFile):
    """Source splitter C++ language specific source code items."""

    def __init__(self, filename: pathlib.Path) -> None:
        """Initialize a new instance of the class.

        Args:
            filename (str): The name of the file.
        """
        super().__init__(filename, SSLANGUAGE_CPP)
        self.import_format = 'include "%s"'
        self.import_suffix = ".hpp"


class SSCSourceFile(SSFunctionLanguageSourceFile):
    """Source splitter C language specific source code items."""

    def __init__(self, filename: pathlib.Path) -> None:
        """Initialize a new instance of the class.

        Args:
            filename (str): The name of the file.
        """
        super().__init__(filename, SSLANGUAGE_C)
        self.import_format = 'include "%s"'
        self.import_suffix = ".h"


SSSFClassMappings = {
    SSLANGUAGE_C: SSCSourceFile,
    SSLANGUAGE_CPP: SSCppSourceFile,
    SSLANGUAGE_JAVA: SSJavaSourceFile,
    SSLANGUAGE_JS: SSJavaScriptSourceFile,
    SSLANGUAGE_PYTHON: SSPythonSourceFile,
    SSLANGUAGE_TS: SSTypeScriptSourceFile,
}


def get_class_for_file(filename: pathlib.Path) -> SSFunctionLanguageSourceFile:
    """Get the class for the language.

    Args:
        filename (Pathlib.Path): The name of the file.

    Returns:
        type[SSFunctionLanguageSourceFile]: The class for the language.

    Raises:
        SSNoLanguageFound: If no language is found.
        SSParseFailed: If the source code cannot be parsed.
    """

    def get_key_from_value(value: str | None) -> str | None:
        if value is None:
            return None
        for key, (extensions, _) in SSLanguageMappings.items():
            if value in extensions:
                return key
        return None

    language = get_key_from_value(filename.suffix)
    if language is None:
        raise SSNoLanguageFound(f"No language found for {filename}")
    try:
        language_type = SSSFClassMappings[str(language)]
    except KeyError as exc:
        raise SSNoLanguageFound(f"No language found for {filename}") from exc
    try:
        sf_instance = language_type(filename)
    except SSParseFailed as e:
        # try alternate language
        if alternate_language := (SSLanguageMappings[language])[1]:
            try:
                sf_instance = SSSFClassMappings[str(alternate_language)](filename)
            except SSParseFailed as exc:
                raise e from exc
        raise e
    return sf_instance
