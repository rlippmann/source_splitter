"""Source Splitter source code items."""

from enum import Enum

SSLANGUAGE_PYTHON = "python"
SSLANGUAGE_JS = "javascript"
SSLANGUAGE_C = "c"
SSLANGUAGE_CPP = "cpp"
SSLANGUAGE_JAVA = "java"
SSLANGUAGE_TS = "typescript"

# Language mappings to extensions.  Key is language, value is set of extensions
# for that language
# 2nd element in the tuple is an alternate possible language
SSLanguageMappings = {
    SSLANGUAGE_PYTHON: ({".py"}, None),
    SSLANGUAGE_JS: ({".js", ".jsx"}, None),
    SSLANGUAGE_C: ({".c", ".h"}, None),
    SSLANGUAGE_CPP: ({".cpp", ".h", ".hpp"}, SSLANGUAGE_C),
    SSLANGUAGE_JAVA: ({".java"}, None),
    SSLANGUAGE_TS: (({".ts", ".tsx"}, SSLANGUAGE_JS)),
}


TS_COMMENT_NODE_TYPES = {"comment", "comment_block", "comment_line"}
TS_IMPORT_NODE_TYPES = {
    "import",
    "import_statement",
    "import_statement_block",
    "import_from_statement",
}
TS_LITERAL_NODE_TYPES = {
    "assignment",
    "string_literal",
    "numeric_literal",
    "const",
    "let",
}
TS_FUNCTION_NODE_TYPES = {"function_definition", "function_declaration"}
TS_METHOD_NODE_TYPES = {"method_definition"}
TS_CLASS_NODE_TYPES = {
    "class_definition",
    "class_declaration",
}
TS_INTERFACE_NODE_TYPES = {"interface_definition"}


# Enum for SourceItem type
class SSSourceItemType(Enum):
    """Enum for item types in SSSourceItem."""

    IMPORT = TS_IMPORT_NODE_TYPES
    LITERAL = TS_LITERAL_NODE_TYPES
    COMMENT = TS_COMMENT_NODE_TYPES
    FUNCTION = TS_FUNCTION_NODE_TYPES
    METHOD = TS_METHOD_NODE_TYPES
    CLASS = TS_CLASS_NODE_TYPES
    INTERFACE = TS_INTERFACE_NODE_TYPES
