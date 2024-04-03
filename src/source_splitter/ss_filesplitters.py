"""File splitter implementation base classes."""

import pathlib
from tree_sitter import Node
from .ss_exceptions import SSNoLanguageFound
from .ss_sourcefile import (
    SSSourceFile,
    SSFunctionLanguageSourceFile,
    SSClassLanguageSourceFile,
    SSInterfaceLanguageSourceFile,
)


class SSFileSplitter:
    """Base class for splitting source code into functions."""

    @staticmethod
    def _write_if_not_exists(path: pathlib.Path, content: str) -> None:
        if path.exists():
            raise ValueError(f"File {path} already exists.")
        path.write_text(content, encoding="utf-8")

    def __init__(
        self, source_file: SSSourceFile, destination_directory: pathlib.Path | None
    ) -> None:
        self._sf = source_file
        self._sfname = self._sf.filename
        self.basename = self._sfname.stem
        self.import_file_name = self._sfname.with_name(
            f"{self.basename}_imports{self._sfname.suffix}"
        )
        self.literal_file_name = self._sfname.with_name(
            f"{self.basename}_literals{self._sfname.suffix}"
        )
        self._stem_prepended = False
        self._destination_directory: pathlib.Path | None = None
        self.main_file: pathlib.Path | None = None
        self.import_list: list[pathlib.Path] = []
        if destination_directory:
            self.destination_directory = destination_directory

    @property
    def use_subdirectories(self) -> bool:
        """Get the use_subdirectories flag."""
        return self._stem_prepended

    @use_subdirectories.setter
    def use_subdirectories(self, value: bool):
        # Check if the value has changed
        if value != self._stem_prepended:
            # Update the include_file path
            self.import_file_name = self._update_path(self.import_file_name, value)
            self.literal_file_name = self._update_path(self.literal_file_name, value)
            self._stem_prepended = value

    def _update_path(
        self, path: pathlib.Path, use_subdirectories: bool
    ) -> pathlib.Path:
        if use_subdirectories and not self._stem_prepended:
            return path.with_name(f"{self.basename}/{path.name}")
        elif not use_subdirectories and self._stem_prepended:
            return path.with_name(path.name[len(path.stem) + 1 :])
        return path

    @property
    def destination_directory(self) -> pathlib.Path | None:
        """Get the destination directory."""
        return self._destination_directory

    @destination_directory.setter
    def destination_directory(self, value: pathlib.Path):
        """Set the destination directory."""
        if not value:
            raise ValueError("Destination directory cannot be None.")
        if not value.is_dir():
            raise ValueError(f"Destination directory {value} is not a directory.")
        self._destination_directory = value.resolve()
        self.main_file = value.joinpath(
            str(self._sfname).replace(self._sfname.suffix, self._sf.import_suffix)
        )

    def split_file(self) -> None:
        """Split the file into literals and imports."""
        self._write_item_file(self._sf.imports, "imports")
        self._write_item_file(self._sf.literals, "literals")
        self._write_main_import_file()

    def _write_main_import_file(self) -> None:
        """Write the top level import file."""
        if not self.main_file:
            raise ValueError("Main file cannot be None.")
        while self.import_list:
            real_import_file = self.import_list.pop(0)
            import_text = self._sf.import_format.format(filename=real_import_file)
            if (
                self._sf.import_directory_specifier
                and self._sf.import_directory_specifier != "/"
            ):
                import_text.replace("/", self._sf.import_directory_specifier)
            if self._sf.import_suffix:
                import_text.replace(self._sf.filename.suffix, self._sf.import_suffix)
            self.main_file.write_text(import_text, encoding="utf-8")

    def _write_item_file(
        self,
        items: list[Node],
        item_name: str | None = None,
    ) -> None:
        """Write the item file."""
        node_name: str | None = None

        if not self.destination_directory:
            raise ValueError("Destination directory cannot be None.")
        for item in items:
            if item_name:
                node_name = item_name
            elif (node_name := self._sf.get_node_name(item)) is None:
                raise ValueError("get_node_name cannot be None.")
            if self.use_subdirectories:
                real_file_name = self.destination_directory.joinpath(
                    self.basename, f"{node_name}{self._sfname.suffix}"
                )
                append_file_name = pathlib.Path(f"{self.basename}/{node_name}")
            else:
                real_file_name = pathlib.Path(
                    f"{self.basename}/_{node_name}{self._sfname.suffix}"
                )
                append_file_name = pathlib.Path(node_name)
            source = self._sf.print_source(item)
            if not item_name:
                self._write_if_not_exists(real_file_name, source)
            else:
                real_file_name.write_text(source, encoding="utf-8")

            self.import_list.append(append_file_name)


class SSFunctionFileSplitter(SSFileSplitter):
    """Base class for splitting source code into functions."""

    def __init__(
        self,
        source_file: SSFunctionLanguageSourceFile,
        destination_directory: pathlib.Path,
    ) -> None:
        super().__init__(self._sf, destination_directory)
        self._sff = source_file

    def split_file(self) -> None:
        super().split_file()
        self._write_item_file(self._sff.functions)
        self._write_main_import_file()


class SSClassFileSplitter(SSFunctionFileSplitter):
    """Base class for splitting source code into classes."""

    def __init__(
        self,
        source_file: SSClassLanguageSourceFile,
        destination_directory: pathlib.Path,
    ) -> None:
        super().__init__(self._sff, destination_directory)
        self._sfc = source_file

    def split_file(self) -> None:
        super().split_file()
        self._write_item_file(self._sfc.classes)
        self._write_main_import_file()


class SSInterfaceFileSplitter(SSClassFileSplitter):
    """Base class for splitting source code into interfaces."""

    def __init__(
        self,
        source_file: SSInterfaceLanguageSourceFile,
        destination_directory: pathlib.Path,
    ) -> None:
        super().__init__(self._sfc, destination_directory)
        self._sfi = source_file

    def split_file(self) -> None:
        super().split_file()
        self._write_item_file(self._sfi.classes)
        self._write_main_import_file()


def get_file_splitter(
    source_file: SSSourceFile, destination_directory: pathlib.Path
) -> SSFileSplitter:
    """Get the splitter for the given source file.

    Args:
        source_file (SSSourceFile): The source file.
        destination_directory (pathlib.Path): The destination directory.

    Returns:
        SSFileSplitter: The splitter for the given source file.

    Raises:
        SSNoLanguageFound: If the source file type is not supported."""
    if isinstance(source_file, SSFunctionLanguageSourceFile):
        return SSFunctionFileSplitter(source_file, destination_directory)
    if isinstance(source_file, SSClassLanguageSourceFile):
        return SSClassFileSplitter(source_file, destination_directory)
    if isinstance(source_file, SSInterfaceLanguageSourceFile):
        return SSInterfaceFileSplitter(source_file, destination_directory)
    raise SSNoLanguageFound(f"Unsupported source file type: {type(source_file)}")
