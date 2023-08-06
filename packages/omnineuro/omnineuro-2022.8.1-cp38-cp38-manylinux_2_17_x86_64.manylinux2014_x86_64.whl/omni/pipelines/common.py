import warnings
import os
import json
import logging
import hashlib
from types import CodeType
from functools import reduce
from typing import Callable, Dict, List, Union
from omni.path import get_wrapped_callable


# raise deprectation warning
warnings.warn("Built-in Pipeline/Stage classes are deprecated. Use memori instead.", DeprecationWarning, stacklevel=2)


class Stage:
    """Stage object representing one node of a processing pipeline.

    Constructs a stage object that wraps a callable for use in a pipeline.
    When the `run` method is called the callable is executed and it's
    return value is stored in a result dictionary that can be accessed
    by the `results` property. The return value is parsed into this
    dictionary based on the list provide by `stage_outputs` (The position
    of each string in the list corresponds to each positional return
    value).

    Note: Stage objects convert their results to JSON so they can be
    written to file. This procedure will convert certain data structures
    (e.g. tuples to list, etc) and give unexpected results if not careful.
    In general, the current workaround is to use JSON compatible data
    structures for your function returns.

    Parameters
    ----------
    function_to_call: Callable
        A callable to wrap that the stage executes.
    stage_outputs: List[str]
        A list of strings to label each return value from the function_to_call.
    hash_output: str
        A directory that should be created or checked to cache the stage execution.
    stage_name: str
        Override the name for the stage.

    Methods
    -------
    run:
        Run the stage.
    """

    def __init__(
        self,
        function_to_call: Callable,
        stage_outputs: List = None,
        hash_output: str = None,
        stage_name: str = None,
        **kwargs,
    ):
        # store function_to_call
        self.function_to_call = function_to_call

        # store function input/output names
        func = get_wrapped_callable(self.function_to_call)
        num_of_input_args = func.__code__.co_argcount
        self.stage_inputs = list(func.__code__.co_varnames[:num_of_input_args])
        self.stage_outputs = stage_outputs if stage_outputs else list()
        self.stage_outputs = (
            stage_outputs
            if type(stage_outputs) == list
            else [
                stage_outputs,
            ]
        )

        # save arguments that should be passed on to the stage
        self.stage_args = kwargs

        # create dictionary for collective stage input arguments
        self.stage_input_args = dict()

        # get the stage name from the function_name
        self.stage_name = stage_name if stage_name else function_to_call.__name__

        # create results dictionary
        self.stage_results = dict()

        # store hash location
        self.hash_output = hash_output

        # create hash file locations
        if hash_output:
            self.stage_hash_location = os.path.join(hash_output, "%s.stage" % self.stage_name)
            self.input_hash_location = os.path.join(hash_output, "%s.inputs" % self.stage_name)
            self.output_hash_location = os.path.join(hash_output, "%s.outputs" % self.stage_name)

    def run(
        self,
        *args,
        force_skip_stage: bool = False,
        force_run_stage: bool = False,
        force_hash_write: bool = False,
        **kwargs,
    ) -> Dict:
        """Call function and save outputs in result dictionary.

        Runs the wrapped function_to_call with given args/kwargs.
        If any kwargs were specified on construction of the stage object,
        they will have precedence over any arguments specified in the
        calling `run` method. Hashes for the stage will also be checked to
        detect whether the stage should be run or not.

        Parameters
        ----------
        force_skip_stage: bool
            Specifies whether this stage should be forcefully skipped
        force_run_stage: bool
            Specifies whether this stage should be forcefully run. Has
            precedence over `force_skip_stage`
        force_hash_write: bool
            Specifies whether the hash for this stage should be written out
            even if the stage has not run.
        """
        # flag that specifies whether the current stage has been run
        self.stage_has_run = False

        # convert args/kwargs into one input arg dictionary
        for i, name in enumerate(self.inputs[: len(args)]):
            self.stage_input_args[name] = args[i]
        self.stage_input_args.update(kwargs)

        # override input_args with any stage_args specified
        self.stage_input_args.update(self.stage_args)
        logging.info("Using these arguments for stage: {}\n{}".format(self.stage_name, self.stage_input_args))

        # initialize stage_should_run
        stage_should_run = True

        # check if hash_output is specified (check if the hashes exists
        # for this stage)
        if self.hash_output:
            # check stage hashes
            hashes_matched = self._check_hashes()

            # if hashes matched, then we want to skip running the stage
            if hashes_matched:
                stage_should_run = False

        # check forcing flags
        if force_skip_stage:
            logging.info("Force skip stage: %s", self.stage_name)
            stage_should_run = False
        if force_run_stage:
            logging.info("Force run stage: %s", self.stage_name)
            stage_should_run = True

        # check stage_should_run
        if stage_should_run:
            logging.info("Running stage: %s", self.stage_name)
            # run the function_to_call with the specified input_args
            outputs = self.function_to_call(**self.stage_input_args)
            # make outputs a list, if not a list/tuple
            if not isinstance(outputs, (tuple, list)):
                outputs = [outputs]
            # make outputs the same length as stage_outputs
            outputs = outputs[: len(self.stage_outputs)]
            # store each output in results dictionary
            for stage_out, out in zip(self.stage_outputs, outputs):
                self.stage_results[stage_out] = out
            # set stage_has_run
            self.stage_has_run = True
        else:
            logging.info("Skipping stage: %s execution...", self.stage_name)
            self._load_results_from_hash()

        # write new hashes after stage has run (or if force_hash_write is set)
        if self.hash_output and (self.stage_has_run or force_hash_write):
            self._write_hashes()

        # return results
        return self.stage_results

    def _load_results_from_hash(self) -> None:
        """Load output hash into results"""
        logging.info("Loading cached results...")
        with open(self.output_hash_location, "r") as f:
            self.stage_results = self._unhash_files_in_dict(json.load(f), "file")

    def _write_hashes(self) -> None:
        """Write hashes of stage to file"""
        self._write_stage_hash(self.stage_hash_location, self._get_function_byte_code)
        self._write_io_hash(self.input_hash_location, self.stage_input_args)
        self._write_io_hash(self.output_hash_location, self.stage_results)

    def _check_hashes(self) -> bool:
        """Check hashes of stage"""
        # check the hash location for the stage hash and the input hash
        stage_match = self._check_stage_hash(self.stage_hash_location, self._get_function_byte_code)
        if not stage_match:
            logging.info("Stage hash for stage: %s did not match!", self.stage_name)
        input_match = self._check_io_hash(self.input_hash_location, self.stage_input_args)
        if not input_match:
            logging.info("Input hash for stage: %s did not match!", self.stage_name)
        # check if output hash exists
        output_hash_exists = os.path.exists(self.output_hash_location)
        if output_hash_exists:
            # load stage results from output hash
            self._load_results_from_hash()
            # Why do we load the results from the output hash then check it against itself?
            # We want to rehash the results available on the disk. It could
            # be different if the user decided to delete/move/modify the output
            # files
            output_match = self._check_io_hash(self.output_hash_location, self.stage_results)

            # check if stage_output keys are in the stage_results
            # this is for cases when the developer adds a new stage output key that is currently
            # not present in the current output hash
            for key in self.stage_outputs:
                if key not in self.stage_results:
                    output_match = False
        else:  # return match False
            output_match = False
        if not output_match:
            logging.info("Output hash for stage: %s did not match!", self.stage_name)

        # return if all checks True or if at least one is False
        return stage_match and input_match and output_hash_exists and output_match

    def _hash_files_in_dict(self, io_dict: Dict) -> Dict:
        """Replaces valid paths in Dict with a special 'file' dict.

        This method replaces valid, existing paths with a dict
        containing the following:

            { "file": file_path, "hash": sha256_hash }

        Parameters
        ----------
        io_dict: Dict
            Dictionary to replace paths with 'file' dict.

        Returns
        -------
        Dict
            A dictionary with all paths replace with 'file' dicts.
        """
        new_dict = io_dict.copy()

        # loop over keys in dictionary
        for key in new_dict:
            # get value at key
            value = new_dict[key]

            # test if value is an existing file
            if isinstance(value, str) and os.path.isfile(value):
                # obtain hash for file
                file_hash = self._hash_file(value)

                # replace with 'file' dict
                new_dict[key] = {"file": value, "hash": file_hash}
            # test if value is another dictionary, run recursive function
            elif isinstance(value, dict):
                new_dict[key] = self._hash_files_in_dict(value)
            # or if the value is a list, then hash each file in the list
            elif isinstance(value, list):
                io_dict[key] = value.copy()  # make a copy of the list so we don't override the original dict
                for i, v in enumerate(value):
                    if type(v) == str and os.path.isfile(v):  # case when entry is a file
                        # obtain hash for file
                        file_hash = self._hash_file(v)

                        # replace with 'file' dict
                        new_dict[key][i] = {"file": v, "hash": file_hash}
                    elif isinstance(v, dict):  # case when entry is another dict
                        new_dict[key][i] = self._hash_files_in_dict(v)

        # return dictionary
        return new_dict

    def _unhash_files_in_dict(self, hash_dict: Dict, xtype: str = "file") -> Dict:
        """Replaces special 'file' dict with hashes or files.

        This method replaces valid a dict containing the following:

            { "file": file_path, "hash": sha256_hash }

        with the value stored at the 'file' or 'hash' key.

        Parameters
        ----------
        hash_dict: Dict
            Dictionary to replace file dict with 'file' or 'hash'.
        xtype: str
            type to replace value with

        Returns
        -------
        Dict
            A dictionary with all file dicts replaced.
        """
        new_dict = hash_dict.copy()

        # loop over keys in dictionary
        for key in new_dict:
            # get value at key
            value = new_dict[key]

            # check if value is a dictionary
            if isinstance(value, dict):
                # check if this dictionary has the 'file' and 'hash' keys
                if "file" in value and "hash" in value:
                    # set the new value for the key based on xtype
                    if xtype == "file":
                        new_dict[key] = value["file"]
                    elif xtype == "hash":
                        new_dict[key] = value["hash"]
                    else:
                        raise ValueError("Invalid xtype.")
                else:  # recursive call on sub dictionary
                    new_dict[key] = self._unhash_files_in_dict(value, xtype)
            elif isinstance(value, list):  # check if value is a list
                hash_dict[key] = value.copy()  # make copy of original list, so we don't overwrite it
                for i, v in enumerate(value):  # loop over values in list
                    if isinstance(v, dict):
                        new_dict[key][i] = self._unhash_files_in_dict({"v": v}, xtype)["v"]  # unhash the value

        # return dictionary
        return new_dict

    def _write_io_hash(self, hash_file: str, io_dict: Dict) -> None:
        """Write input/output hash to file.

        Parameters
        ----------
        hash_file: str
            Location of hash file to write to
        io_dict: Dict
            Input Dictionary
        """
        os.makedirs(os.path.dirname(hash_file), exist_ok=True)
        with open(hash_file, "w") as f:
            json.dump(self._hash_files_in_dict(io_dict), f, sort_keys=True, indent=4)

    def _check_io_hash(self, hash_file: str, current_io_dict: Dict) -> bool:
        """Return if current input/output hash matches input dict of stage

        Parameters
        ----------
        hash_file: str
            Location of hash file to compare current input/output dict to.
        current_io_dict: Dict
            Input/Output dictionary to stage.
        """
        # get hashes for current io dict
        current_hash_dict = self._hash_files_in_dict(current_io_dict)
        # check if hash_file exists
        if os.path.exists(hash_file):
            try:
                with open(hash_file, "r") as f:
                    io_hash_from_file = self._unhash_files_in_dict(json.load(f), "hash")
                    return io_hash_from_file == self._unhash_files_in_dict(current_hash_dict, "hash")
            except json.JSONDecodeError:  # corrupted JSON
                return False
        else:  # No hash file exists at location
            return False

    @staticmethod
    def _write_stage_hash(hash_file: str, stage_bytes: bytes) -> None:
        """Writes stage hash to file

        Parameters
        ----------
        hash_file: str
            Location of hash file to write to
        stage_bytes: bytes
            Byte value of stage function
        """
        os.makedirs(os.path.dirname(hash_file), exist_ok=True)
        with open(hash_file, "wb") as f:
            f.write(stage_bytes)

    @staticmethod
    def _check_stage_hash(hash_file: str, current_stage_bytes: bytes) -> bool:
        """Return True/False if current stage hash matches current stage bytes

        Parameters
        ----------
        hash_file: str
            Location of hash file to compare current stage bytes to
        current_stage_bytes: bytes
            Byte value of stage function to call
        """
        # check if hash_file exists
        if os.path.exists(hash_file):
            # compare the hash file
            with open(hash_file, "rb") as f:
                stage_hash_from_file = f.read()
                return stage_hash_from_file == current_stage_bytes
        else:  # No hash file exists at location
            return False

    @staticmethod
    def _hash_file(filename: str) -> str:
        """Hash file

        Parameters
        ----------
        filename: str
            Filename to hash.

        Returns
        -------
        str
            Hash of file.
        """
        # initialize sha256 hasher
        hasher = hashlib.sha256()

        # open file and hash
        with open(filename, "rb") as f:
            hasher.update(f.read())

        # return the hash
        return hasher.hexdigest()

    @property
    def _get_function_byte_code(self) -> bytes:
        """Get bytes of from function code object for hashing."""
        # return get_wrapped_callable(self.function_to_call).__code__.co_code
        return get_func_hash(self.function_to_call)

    @property
    def inputs(self) -> List[str]:
        """List[str]: A list of input argument names for the stage."""
        return self.stage_inputs

    @property
    def outputs(self) -> List[str]:
        """List[str]: A list of output argument names for the stage."""
        return self.stage_outputs

    @property
    def args(self) -> Dict:
        """Dict: A dictionary of only the provided input arguments to the
        stage on construction."""
        return self.stage_args

    @property
    def input_args(self) -> Dict:
        """Dict: A dictionary of all input arguments to the stage. Is only
        populated after the `run` method is invoked."""
        return self.stage_input_args

    @property
    def results(self) -> Dict:
        """Dict: A dictionary of the output return values for the stage."""
        return self.stage_results

    @property
    def state(self) -> bool:
        """bool: A flag that specifies whether the current stage has been run
        (The callable has executed)."""
        return self.stage_has_run


class Pipeline:
    """This class defines a processing pipeline linking multiple Stages.

    The definition list accepts a tuple of Stage objects with the
    following syntax:

    Examples
    --------
    >>> # the start keyword is for stages that do not have input from other stages
    >>> spec = [("start", stage0), (stage0, stage1), ((stage0, stage1), stage2)]
    >>> # last entry has multiple inputs to another stage
    >>> # create the pipeline object
    >>> pipeline = Pipeline(spec)
    >>> # run the pipeline
    >>> pipeline.run()

    Stages are run in the order that they are defined in (In the example above: stage0 -> stage1 -> stage2).

    Parameters
    ----------
    definition: List
        A list of tuples containing Stage objects that define how a pipeline is connected.

    Methods
    -------
    run:
        Runs the pipeline.
    """

    def __init__(self, definition: List):
        # save the pipeline definition
        self.definition = definition

        # verify that all inputs are stage objects
        stages = list()  # dump all pipeline definitions into single list
        for input_stages, output_stages in self.definition:
            if not isinstance(input_stages, tuple):
                input_stages = (input_stages,)
            stages.append(output_stages)
            stages.extend(input_stages)
        for stage in stages:  # check stages for invalid type
            if not (isinstance(stage, Stage) or stage == "start"):
                raise ValueError("Found invalid input %s to pipeline definition!" % stage)

        # initialize results
        self.pipeline_results = dict()

    def run(self, *args, **kwargs) -> None:
        """Runs the pipeline. Any stages linked to a "start" keyword accepts
        the input args/kwargs from this run method call.
        """
        for input_stages, stage_to_run in self.definition:
            # check in input_stages is a "start" stage
            if input_stages == "start":
                # use input args/kwargs for calling stage
                stage_to_run.run(*args, **kwargs)
            else:  # find the inputs required from the input stages
                # create dictionary for input arguments
                input_args = dict()

                # make input_stages a tuple if not already one
                if not isinstance(input_stages, tuple):
                    input_stages = (input_stages,)

                # combine all results from input_stages into one dictionary
                combined_results = dict()
                for s in input_stages:
                    combined_results.update(s.results)
                combined_results.update(stage_to_run.args)

                # loop through calling stage inputs
                for arg in stage_to_run.inputs:
                    # get matching argument from combined results
                    try:
                        input_args[arg] = combined_results[arg]
                    except KeyError:  # ignore KeyErrors
                        # Let any argument exceptions be handled by python
                        pass

                # run the stage with the input_args
                try:
                    stage_to_run.run(**input_args)
                except Exception as error:
                    # give some debugging info to diagnosis why this stage
                    # failed to run
                    print("\n\ninput_args: %s" % input_args)
                    print("\n\npipeline_results: %s\n\n" % combined_results)

                    # reraise exception
                    raise error

            # update pipeline results
            self.pipeline_results.update(stage_to_run.results)

        # return results
        return self.pipeline_results

    @property
    def results(self) -> Dict:
        """Dict: A dictionary of the output return values for the pipeline."""
        return self._get_abspaths(self.pipeline_results)

    def _get_abspaths(self, dictionary: Dict):
        """Convert all valid paths in dictionary to absolute path"""
        new_dict = dictionary.copy()

        # loop over keys in dictionary
        for key in new_dict:
            # get value at key
            value = new_dict[key]

            # test if value is an existing file
            if isinstance(value, str) and os.path.isfile(value):
                # convert path to absolute path
                new_dict[key] = os.path.abspath(value)
            # test if value is another dictionary, run recursive function
            elif isinstance(value, dict):
                new_dict[key] = self._get_abspaths(value)

        # return dictionary
        return new_dict


def redefine_result_key(dictionary: Dict, from_key: str, to_key: str) -> Dict:
    """Redefines a result key in the dictionary to a different key.

    Examples
    --------
    >>> dictionary = {"hello": 1, "test": 2}
    >>> new_dict = redefine_result_key(dictionary, "hello", "testing")
    >>> # new_dict is now: {"testing": 1, "test": 2}

    Parameters
    ----------
    dictionary: Dict
        Dictionary to change key of.
    from_key: str
        Key to change.
    to_key: str
        Key to replace with.

    Returns
    -------
    Dict
        New dictionary with replaced keys.
    """
    # get dictionary
    new_dict = dictionary.copy()

    # assign to_key, from_key value
    new_dict[to_key] = dictionary[from_key]

    # delete from key
    del new_dict[from_key]

    # return dictionary
    return new_dict


def get_func_hash(func: Union[Callable, CodeType]) -> bytes:
    """Hashes a function into unique bytes.

    This function grabs relevant bytes from the
    function code object for hashing. It is ordered as
    the following:

        consts, methods, code

    In consts, the doc sting of the code object is removed
    and any embedded code objects are appended to the end
    of bytes array.

    Parameters
    ----------
    func: Union[Callable, CodeType]
        Function to hash.

    Returns
    -------
    bytes
        Unique bytes representing the function.
    """
    # check if function or code object
    if "__code__" in func.__dir__():  # this is a function
        # unwrap the function if any wrappers exist
        func = get_wrapped_callable(func)

        # get the consts, methods and code of the function
        consts = func.__code__.co_consts[1:]  # drop element 1, the doc string
        methods = func.__code__.co_names
        code = func.__code__.co_code

        # get a reference to code object type
        code_object_type = type(func.__code__)
    else:  # this is a code object
        # get the consts, methods and code of the function
        consts = func.co_consts[1:]  # drop element 1, the doc string
        methods = func.co_names
        code = func.co_code

        # get a reference to code object type
        code_object_type = type(func)

    # loop through the consts, if another code object exists in
    # it delete it from consts and recursively call this function on it.
    filtered_consts = list()
    embedded_code_objects = list()
    for c in consts:
        if code_object_type == type(c):  # check if code object
            embedded_code_objects.append(get_func_hash(c))  # record hash
        else:  # add to the new list
            filtered_consts.append(c)

    # convert back to tuple
    consts = tuple(filtered_consts)

    # convert to bytes
    consts = str(consts).encode("utf-8")
    methods = str(methods).encode("utf-8")

    # return concatenated bytes
    bytes_list = [consts, methods, code] + embedded_code_objects
    return reduce(lambda x, y: x + y, bytes_list)
