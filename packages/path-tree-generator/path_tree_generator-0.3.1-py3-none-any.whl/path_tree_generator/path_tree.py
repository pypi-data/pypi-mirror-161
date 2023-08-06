"""
Path Tree Generator
"""
import pathlib

from path_tree_generator.models.list_entries import ListEntry, ListEntryType


class PathTree:
    def __init__(
            self,
            root_dir: str | pathlib.Path,
            relative_paths=True,
            paths_as_posix=False,
            read_stat=False,
    ):
        """ `PathTree` class for generating tree-like directory listings also for humans
        and output them as `str`, `list[str]`, `dict` or `json`.

        :param root_dir: Root directory, from where to start the tree generator.
        :param relative_paths: Generate relative paths bases on the root_dir, especially for dict and json.
        :param paths_as_posix: Uses string representation of the paths with forward (/) slashes.
        :param read_stat: Read the files or directories stat and set them in the `ListElement`s of `PathTree`
        """
        self._root_dir = root_dir
        if isinstance(root_dir, str):
            self._root_dir = pathlib.Path(root_dir)
        self._relative_paths = relative_paths
        self._paths_as_posix = paths_as_posix
        self._read_stat = read_stat

        self._generator = _PathTreeGenerator(
            root_dir=self._root_dir,
            relative_paths=self._relative_paths,
            paths_as_posix=self._paths_as_posix,
            read_stat=self._read_stat,
        )

    def dict(self, exclude_unset=False, exclude_defaults=False, exclude_none=False) -> dict:
        """ `dict` representation of a directory tree (`PathTree`)

        :param exclude_unset: Whether fields which were not set should be excluded
        :param exclude_defaults: Whether fields which are equal to their default values should be excluded.
        :param exclude_none: Whether fields which are equal to None should be excluded.
        :return: A dict
        """
        tree = self._generator.tree()
        return tree.dict(
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    def json(self, exclude_unset=False, exclude_defaults=False, exclude_none=False) -> str:
        """ `json` representation of a directory tree (`PathTree`)

        :param exclude_unset: Whether fields which were not set should be excluded
        :param exclude_defaults: Whether fields which are equal to their default values should be excluded.
        :param exclude_none: Whether fields which are equal to None should be excluded.
        :return: A json string
        """
        tree = self._generator.tree()
        return tree.json(
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    def human_readable(self) -> str:
        """ Human readable string representation of a directory tree (`PathTree`)

        :return: A string
        """
        return self._generator.tree_human_readable(root_dir_name_only=True)

    def human_readable_list(self) -> list:
        """ Human readable string list representation of a directory tree (`PathTree`)

        :return: A list of strings
        """
        return self._generator.tree_human_readable_list(root_dir_name_only=True)

    def tree(self) -> ListEntry:
        """ `ListEntry` representation of a directory tree (`PathTree`)

        :return: `ListEntry` object
        """
        return self._generator.tree()


class _PathTreeGenerator:
    HR_DIR_PREFIX = "["
    HR_DIR_SUFFIX = "]"
    HR_PIPE = "│"
    HR_ELBOW = "└──"
    HR_TEE = "├──"
    HR_PIPE_PREFIX = "│   "
    HR_SPACE_PREFIX = "    "

    def __init__(
            self,
            root_dir: pathlib.Path,
            relative_paths=True,
            paths_as_posix=False,
            read_stat=False,
    ):
        self._root_dir = root_dir
        self._relative_paths = relative_paths
        self._paths_as_posix = paths_as_posix
        self._read_stat = read_stat

        self._tree_list: list[ListEntry] = []
        self._tree_dict: dict[ListEntry] = {}
        self._tree_built = False
        self._hr_tree_list: list[str] = []
        self._hr_tree_built = False

    def tree(self) -> ListEntry:
        self._build_tree(self._root_dir)

        path = self._root_dir

        if self._relative_paths:
            path = self._root_dir.relative_to(self._root_dir)

        if self._paths_as_posix:
            path = path.as_posix()

        entry = ListEntry(
            entry_type=ListEntryType.dir,
            name=self._root_dir.name,
            path=path,
            children=self._tree_list,
        )

        if self._read_stat:
            total_size = 0
            if entry.children:
                for child in entry.children:
                    total_size += child.stat.size
            if self._root_dir.exists():
                entry.add_stat_result(
                    stat=self._root_dir.stat(),
                    size=total_size,
                )

        return entry

    def tree_human_readable(self, root_dir_name_only=True) -> str:
        self._build_hr_tree(root_dir_name_only=root_dir_name_only)
        return '\n'.join(self._hr_tree_list)

    def tree_human_readable_list(self, root_dir_name_only=True) -> list[str]:
        self._build_hr_tree(root_dir_name_only=root_dir_name_only)
        return self._hr_tree_list

    def _build_tree(self, path: pathlib.Path):
        if self._tree_built:
            return

        entries = self._prepare_entries(path)
        if entries:
            self._tree_list = entries

        self._tree_built = True

    def _prepare_entries(self, path: pathlib.Path) -> list[ListEntry] | None:
        entries: list[ListEntry] = []
        if path.is_dir():
            for entry in path.iterdir():
                if entry.is_dir():
                    entries.append(
                        self._dir_entry(entry)
                    )
                if entry.is_file():
                    entries.append(
                        self._file_entry(entry)
                    )
        if entries:
            return entries

    def _dir_entry(self, path: pathlib.Path):
        _path = path
        path_name = path.name

        if self._relative_paths:
            try:
                path = path.relative_to(self._root_dir)
            except ValueError:
                path = path

        if self._paths_as_posix:
            path = path.as_posix()

        entry = ListEntry(
            entry_type=ListEntryType.dir,
            name=path_name,
            path=path,
            children=self._prepare_entries(_path),
        )

        if self._read_stat:
            total_size = 0
            if entry.children:
                for child in entry.children:
                    total_size += child.stat.size
            if _path.exists():
                entry.add_stat_result(
                    stat=_path.stat(),
                    size=total_size,
                )

        return entry

    def _file_entry(self, path: pathlib.Path):
        entry = ListEntry(
            entry_type=ListEntryType.file,
            name=path.name,
            path=path,
        )

        if self._read_stat:
            entry.add_stat_result(
                stat=path.stat(),
            )

        if self._relative_paths:
            try:
                path = path.relative_to(self._root_dir)
                entry.path = path
            except ValueError:
                path = path

        if self._paths_as_posix:
            entry.path = path.as_posix()

        return entry

    def _build_hr_tree(self, root_dir_name_only=True):
        self._build_tree(self._root_dir)
        if self._hr_tree_built:
            return
        self._hr_tree_head(root_dir_name_only=root_dir_name_only)
        self._hr_tree_body(self._tree_list)
        self._hr_tree_built = True

    def _hr_tree_head(self, root_dir_name_only=True):
        tree_head = self._root_dir.name if root_dir_name_only else self._root_dir
        self._hr_tree_list.append(
            f'{self.HR_DIR_PREFIX}{tree_head}{self.HR_DIR_SUFFIX}'
        )
        # self._hr_tree_list.append(self.PIPE)  # add additional space

    def _hr_tree_body(self, children, prefix=''):
        # entries = self._hr_prepare_entries(children)
        entries_count = len(children)
        for index, entry in enumerate(children):
            entry: ListEntry
            connector = self.HR_ELBOW if index == entries_count - 1 else self.HR_TEE
            if entry.entry_type == ListEntryType.dir:
                self._hr_add_directory(
                    entry, index, entries_count, prefix, connector
                )
            else:
                self._hr_add_file(entry, prefix, connector)

    def _hr_add_directory(
            self,
            entry: ListEntry,
            index,
            entries_count,
            prefix,
            connector,
    ):
        self._hr_tree_list.append(
            f'{prefix}{connector} {self.HR_DIR_PREFIX}{entry.name}{self.HR_DIR_SUFFIX}'
        )

        if index != entries_count - 1:
            prefix += self.HR_PIPE_PREFIX
        else:
            prefix += self.HR_SPACE_PREFIX

        if entry.children is not None:
            self._hr_tree_body(
                children=entry.children,
                prefix=prefix,
            )
        # self._hr_tree_list.append(prefix.rstrip())

    def _hr_add_file(
            self,
            file,
            prefix,
            connector
    ):
        self._hr_tree_list.append(f'{prefix}{connector} {file.name}')
