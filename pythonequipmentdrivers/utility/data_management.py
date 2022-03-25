import json
from dataclasses import dataclass, field
from itertools import zip_longest
from pathlib import Path
from time import asctime, strftime
from typing import Any, Dict, Iterable, List, Optional

__all__ = ("log_to_csv", "dump_data", "dump_array_data", "create_test_log",
           "Logger")


def log_to_csv(file_path: Path, *data: Any, init: bool = False) -> None:
    """
    log_to_csv(file_path, *data, init=False)

    Writes an iterable to a row of a csv file. Useful for logging data row by
    row while a test or measurement is in progress.

    If init=True a new file is created (or overwriten if the file already
    exists) and the iterable "data" is unpacked into the first row of the new
    document. If init = False then the existing file is opened and the iterable
    "data" is unpacked and appended to the end of the document. If init = False
    but the file does not already exist it will be created.

    The arguement "file_path" specifies the path of the file to be
    created/updated. The log file will be storted at file_path.csv, if the
    "csv" extension is not present it will be added automatically.

    The iterable "data" can contain an arbitrary number of elements and each
    element can use an arbitrary data type as long as it can be safely cast to
    a string. The argument "data" should be passed as an unpacked structure,
    not as an iterable. For example:

        Correct:
            log_to_csv("my_data", 1, 2, 3, 4, 5)
            log_to_csv("my_data", *list_of_data)
            log_to_csv("my_data", *['a', 'b', 'c', 4, 5, 6])
            log_to_csv("my_data", *(1, 2, 3, 4, 5))
            log_to_csv("my_data", 'column 1', 'column 2', init=True)

        Incorrect:
            log_to_csv("my_data", [1, 2, 3, 4, 5])
            log_to_csv("my_data", ('a', 'b', 'c', 'd'))

    In the case of the incorrect examples the entire iterable "data" would be
    stored in a single cell of the csv file.

    Args:
        file_path (str, or path-like object): path of the log file to use, does
            not need to include the file extension or previously exist.
        data: a sequence or unpacked iterable of data to be stored.

    Kwargs:
        init (bool, optional): Whether or not to open the log file in write
            mode ("True", for creating a new file) or append mode ("False" for
            adding additional data). Defaults to False.
    Example:
        cwd = Path().parent.resolve()
        file = cwd.joinpath('my_data')
        mydata = [3, 4, 5]
        moredata = {6, 7, 8}
        log_to_csv(file, "column A", "column B", "column C", init=True)
        log_to_csv(file, 1, 2, 3)
        log_to_csv(file, *mydata)  # note use of list unpacking
        log_to_csv(file, *moredata)  # note use of set unpacking
    """

    file_path = Path(file_path)
    # add/correct file extension
    file_path_ext = file_path.parent / f'{file_path.stem}.csv'

    if init:
        file_path_ext.touch()  # create file

    with open(file_path_ext, 'w' if init else 'a') as f:
        print(*data, sep=',', file=f)


def dump_data(file_path: Path, data: Iterable[Iterable[Any]]) -> None:
    """
    dump_data(directory, file_name, data)

    Writes an iterable of iterables, such as a list of lists, row by row to a
    csv file. Useful for logging a large chunk of data at once after test or
    measurement.

    The arguement "file_path" specifies the path of the file to be created. The
    log file will be storted at file_path.csv, if the "csv" extension is not
    present it will be added automatically.

    The iterable "data" can contain an arbitrary number of elements which in
    turn can have arbitrary length and data type as long as it can be safely
    cast to a string. For example:

        data = [["column A", "column B", "column C"], [1, 2, 3], [4, 5, 6]]
        dump_data("some_directory\\my_data", data)

    Each element of data does not need to have the same length but it is
    recommended to make parsing the data after the fact easier.

    Args:
        file_path (str, or path-like object): path of the log file to use, does
            not need to include the file extension or previously exist.
        data (Iterable[Iterable[Any]]): an iterable of iterables of data to be
            stored. Each element should be able to be cast to string.

    Returns:
        NoneType
    """

    file_path = Path(file_path)

    # add/correct file extension
    file_path_ext = file_path.parent / f'{file_path.stem}.csv'
    file_path_ext.touch()  # create file

    with open(file_path_ext, 'w') as f:

        for item in data:
            print(*item, sep=',', file=f)


def dump_array_data(file_path: Path,
                    data: Iterable[Iterable[any]],
                    init: bool = False,
                    fill_value: Optional[str] = None) -> None:
    """
    dump_array_data(file_path, data, init=False, longest=False,
    fill_value=None)

    Writes a iterable of iterables to rows of a csv file by transposing them.
    Useful for logging data contained in multiple arrays, row by row after
    a test or measurement completes.
    if fill_value is not None, will pad with fill_value, default None

    example:


    If init=True a new file is created (or overwriten if the file already
    exists) and the iterable "data" is unpacked into the first row of the new
    document. If init = False then the existing file is opened and the iterable
    "data" is unpacked and appended to the end of the document. If init = False
    but the file does not already exist it will be created.

    The arguement "file_path" specifies the path of the file to be
    created/updated. The log file will be storted at file_path.csv
    , file_path itself does not need to contain the file extension, it will
    automatically be added.

    The iterable "data" can contain an arbitrary number of elements and each
    element can use an arbitrary data type as long as it can be safely cast to
    a string. The argument "data" SHOULD be passed as a PACKED structure,
    i.e. AS an iterable. For example:

        Incorrect:
            dump_array_data("my_data", 1, 2, 3, 4, 5)
            dump_array_data("my_data", *list_of_data)
            dump_array_data("my_data", *['a', 'b', 'c', 4, 5, 6])
            dump_array_data("my_data", *(1, 2, 3, 4, 5))
            dump_array_data("my_data", 'column 1', 'column 2', init=True)

        Correct:
            dump_array_data("my_data", [1, 2, 3, 4, 5])
            dump_array_data("my_data", (['a', 'b', 'c', 'd'], [1, 2, 3, 4, 5]),
                            init=True)

    Args:
        file_name (str, or path-like object): path of the log file to use, does
            not need to include the file extension or previously exist.
        data: an iterable of data to be stored.

    Kwargs:
        init (bool, optional): Whether or not to open the log file in write
            mode ("True", for creating a new file) or append mode ("False" for
            adding additional data). Defaults to False.
    Example:
        cwd = Path().parent.resolve()
        file = cwd.joinpath('my_data')
        list1 = ['a', 'b', 'c', 'd', 'e']
        list2 = [1, 2, 3, 4, 5, 6, 7, 8]
        list3 = [4, 5, 6, 7, 8, 9]
        args = (list1, list2, list3)
        dump_array_data(file, args, fill_value='')

        outputs as:
        a,1,4
        b,2,5
        c,3,6
        d,4,7
        e,5,8
        '',6,9
        '',7,''
        '',8,''

    """

    file_path = Path(file_path)
    file_path_ext = file_path.parent / f'{file_path.stem}.csv'

    if fill_value is not None:  # create generator
        rows = zip_longest(*data, fillvalue=fill_value)
    else:
        rows = zip(*data)

    with open(file_path_ext, 'w' if init else 'a') as f:
        print(*rows, sep=',', end='\n', file=f)


def create_test_log(base_dir, images=False, raw_data=False, **test_info):
    """
    create_test_log(base_dir, images=False, raw_data=False, **test_info)

    Creates a directory structure to be used for storing test data or
    measurements.

    The directory structure is created in the root directory
    specified by the arguement "base_dir". By default the name of the resulting
    directory will be "test_data_TIMESTAMP" where TIMESTAMP is record of when
    the directory was created in the format YYYYMMDDHHmmSS. To change the name
    of the directory structure pass an alternate name using the arguement
    "test_name". The timestamp is not optional and will always be added, this
    is included to prevent the accidently overwrite of data.

    Two additional sub-directories can be created within the directory
    structure by setting their boolean arguements "images" and "raw_data" to
    True. These arguements will create sub-folders with the same names within
    the directory structure. These directories are intended for storing images
    and raw data files respectively, in a more orgainized manner than in a flat
    directory.

    If any keyword arguements are passed they will be logged in a json file
    within the directory structure called "log_TIMESTAMP.json" This is intened
    to hold the configuration settings or any notes for a test or experiment
    that is to be run. In addition to any keyword arguements passed an addition
    key-value pair, ('run_time': TIMESTAMP) will be added to the json.

    Example:

    # The following code ...

        test_info = {'test_name': 'Transient_Measurements',
                     'v_in_setpoints': [40, 54, 60],
                     'i_out_setpoints': [100, 200, 300],
                     'measurement_delay': 2.0,
                     'dut': "SN0123456789"}
        create_test_log("example_dir", images=True, **test_info)

    # ... produces the directory structure below:

        example_dir |
                    |
                    ___ Transients_20210521095931 |
                                                  |
                                                  __ images
                                                  |
                                                  |
                                                  __ log_20210521095931.json

    Args:
        base_dir (str or Path-like object): root directory in which to create
            the directory structure.
        images (bool, optional): Whether or not to create a sub-directory
            called "images". Defaults to False.
        raw_data (bool, optional): Whether or not to create a sub-directory
            called "raw_data". Defaults to False.
    Kwargs:
        test_info: configuration information for a test or experiment. Can
            include an alternate name for the directory structure with the key
            "test_name". Will be logged to a json file

    Returns:
        Path-like object: The path to the newly created directory structure.
    """

    test_name = test_info.get('test_name', 'test_data')
    file_t_stamp = strftime(r"%Y%m%d%H%M%S")
    test_info['run_time'] = strftime(r"%Y/%m/%d %H:%M:%S")

    # make base directory for test log
    test_dir = Path(base_dir) / f'{test_name}_{file_t_stamp}'
    test_dir.mkdir(exist_ok=False)  # arg prevents accidently overwriting

    # optional sub-directories for images or raw data files
    if images:
        (test_dir / 'images').mkdir()
    if raw_data:
        (test_dir / 'raw_data').mkdir()

    # dump config dictionary to file if kwargs were passed
    if test_info:
        with open(test_dir / f'{test_name}_{file_t_stamp}.json', 'w') as f:
            json.dump(test_info, f, indent=4,
                      check_circular=True,
                      allow_nan=True,
                      sort_keys=False)

    return test_dir  # return newly created directory


@dataclass
class LoggerFileDirectory:
    """file directory structure object for a Logger instance"""
    root_dir: Path
    message_log_path: Path = field(init=False)
    data_log_path: Path = field(init=False)
    image_dir: Path = field(init=False)
    raw_data_dir: Path = field(init=False)
    metadata_path: Path = field(init=False)

    def __post_init__(self):
        self.root_dir = Path(self.root_dir).resolve()

        self.message_log_path = self.root_dir.joinpath('message_log.txt')
        self.data_log_path = self.root_dir.joinpath('data.csv')
        self.image_dir = self.root_dir.joinpath('images')
        self.raw_data_dir = self.root_dir.joinpath('raw_data')
        self.metadata_path = self.root_dir.joinpath('metadata.json')


class Logger:

    def __init__(self, root_dir: Path,
                 print_messages: bool = True,
                 log_table_data: bool = False,
                 log_images: bool = False,
                 log_raw_data: bool = False,
                 **metadata) -> None:
        """
        Creates a file logging object that can log information to file while
        also printing it to screen (optional)

        Args:
            root_dir (str or Path-like object): root directory in which to
                create the directory structure for the logger.
            log_table_data (bool, optional): If true it will create a csv to
                log tabular data. Defaults to False.
            log_images (bool, optional): If true it will create a subdirectory
                at root_dir called images store any image files. Defaults to
                False.
            log_raw_data (bool, optional): If true it will create a
                subdirectory called "raw_data" to large unprocessed blocks of
                data such as waveforms. Defaults to False.
            print_messages (bool, optional): Whether or not to print the log
                messages to the terminal in addition to writing them to file.
                Defaults to True.
        Kwargs:
            If any kwargs are passed, will be logged to a json file titled
            metadata.json at the specified root_dir. If no kwargs are passed a
            file will not be created
        """

        self.print_messages = print_messages
        self.log_table_data = log_table_data
        self.log_images = log_images
        self.log_raw_data = log_raw_data

        # setup directory structure
        self.file_directory = LoggerFileDirectory(root_dir)

        # check whether the directory structure exists already (resuming a
        # session), or if they need to be created

        messages: List[str] = []  # batch messages so file can be opened once

        if self._is_existing_log_present():
            if not self._can_resume_log():
                raise Exception('Logging session can only be resumed if the '
                                'same directory structure is used')

            messages.append(f'({asctime()}) Resuming existing logging session')
        else:
            parent_dir = self.file_directory.root_dir.parent
            self.file_directory.message_log_path.touch(exist_ok=False)
            messages.append(
                f'({asctime()}) Message Log Created\n\t'
                f'{self.file_directory.message_log_path.relative_to(parent_dir)}')

            if log_table_data:
                self.file_directory.data_log_path.touch(exist_ok=False)
                messages.append(
                    'Tabular data log created Log Created: \n\t'
                    f'{self.file_directory.data_log_path.relative_to(parent_dir)}'
                    )

            if log_images:
                self.file_directory.image_dir.mkdir(exist_ok=False)
                messages.append(
                    'Image subdirectory created: \n\t'
                    f'{self.file_directory.image_dir.relative_to(parent_dir)}'
                    )

            if log_raw_data:
                self.file_directory.raw_data_dir.mkdir(exist_ok=False)
                messages.append(
                    'Raw Data subdirectory created: \n\t'
                    f'{self.file_directory.raw_data_dir.relative_to(parent_dir)}'
                    )

        if metadata:
            self.log_metadata(**metadata)

        self.log_message(*messages)

    def _can_resume_log(self) -> bool:
        """
        Checks to see if an logging session can be resumed, for this to be
        true the specified directory structure must already exist, and none of
        the needed files/directories can be missing from self.root_dir
        """
        # if the full directory structure is there then the log can be resumed

        criteria = (
            self.log_table_data ^ self.file_directory.data_log_path.exists(),
            self.log_images ^ self.file_directory.image_dir.exists(),
            self.log_raw_data ^ self.file_directory.raw_data_dir.exists()
        )

        can_resume = not any(criteria)
        return can_resume

    def _is_existing_log_present(self) -> bool:
        """
        Checks self.root_dir to see if there's an existing logging
        session
        """
        return self.file_directory.message_log_path.exists()

    def log_message(self, *messages: str) -> None:
        """
        Logs an arbitrary number of arguments to the log file as str, arguments
        are written to file/printed seperated by newline chars. If the argument
        is not of type str it will be cast to str before writing to file.
        """

        with open(self.file_directory.message_log_path, 'a') as file:
            print(*messages, sep='\n', end='\n', file=file)

        if self.print_messages:
            print(*messages, sep='\n')

    def log_data(self, *data: Any) -> None:
        """logs an arbitrary number of arguments to a new row in a csv file"""

        if not self.log_table_data:
            message = ('Attempted to log data to non-existing file. '
                       'Configure logger with "log_table_data" when '
                       'instantiating to log data')
            self.log_message(message)
            raise IOError(message)

        log_to_csv(self.file_directory.data_log_path, *data)

    def log_metadata(self, **metadata) -> None:
        existing_metadata = self.get_metadata()  # could be empty dict

        # add new metadata to existing metadata
        # allowing new values to overwrite the old ones
        for key, value in metadata.items():
            existing_metadata[key] = value

        # save to file
        with open(self.file_directory.metadata_path, 'w') as file:
            json.dump(existing_metadata, file, indent=4, check_circular=True,
                      allow_nan=True, sort_keys=False)

    def get_metadata(self) -> Dict[str, Any]:
        if not self.file_directory.metadata_path.exists():
            return dict()

        with open(self.file_directory.metadata_path, 'r') as file:
            metadata = json.load(file)
        return metadata
