from pathlib import Path
import logging
from typing import Callable, List
from bids import BIDSLayout
from .preprocessing import pre_proc
from memori.pathman import get_prefix


def bids_proc(
    bids_path: str,
    output_path: str,
    participant_label: List[str],
    function_to_run: Callable = pre_proc,
    combine_sessions: bool = False,
    skip_validation: bool = False,
    database: str = None,
    reset_database: bool = False,
    skip_database: bool = False,
    dryrun: bool = False,
    single_rest_run: bool = False,
    **kwargs,
) -> None:
    """BIDS processor.

    Parameters
    ----------
    bids_path : str
        Path to BIDS dataset.
    output_path : str
        Path to output files.
    participant_label : List[str]
        List of participant labels to process.
    function_to_run: Callable
        Function to run. Must take the following arguments: output_path, t1, t2, func, metadata, kwargs
    skip_validation : bool
        Skip BIDS validator.
    database : str
        Path to alternative location for BIDS sql database.
    reset_database : bool
        Delete the current BIDS sql database.
    skip_database : bool
        Skip reading/writing from BIDS data sql database.
    dryrun : bool
        Run bids parsing, but don't do any processing.
    single_rest_run : bool
        If True, only process the first rest run (For paper).
    """
    # keep bids path in kwargs just in-case we need it again
    kwargs["bids_path"] = bids_path

    # create a layout
    layout = BIDSLayout(
        bids_path,
        validate=not skip_validation,
        database_path=None if skip_database else database,
        reset_database=reset_database,
    )

    # if participant label not defined get all subjects
    if not participant_label:
        participant_label = layout.get_subjects()
    logging.info("Subjects in dataset: %s", participant_label)

    # create dictionary for loop through files
    bids_dict = dict()

    # loop over all subjects
    for subject in participant_label:
        # get all sessions for subject
        sessions = layout.get_sessions(subject=subject)
        sessions.sort()
        logging.info("Found these sessions for subject %s: %s", subject, sessions)

        # add subject in to dictionary
        bids_dict[subject] = dict()

        # loop over sessions
        for session in sessions:
            # add session to dict
            bids_dict[subject][session] = dict()

            # subject and session
            sub_ses = {"subject": subject, "session": session, "extension": "nii.gz"}

            # get t1/t2/func for subject/session
            t1 = layout.get(datatype="anat", suffix="T1w", **sub_ses)
            t2 = layout.get(datatype="anat", suffix="T2w", **sub_ses)
            func = layout.get(datatype="func", **sub_ses)

            # sort lists
            t1.sort(key=lambda f: f.filename)
            t2.sort(key=lambda f: f.filename)
            func.sort(key=lambda f: f.filename)

            # add t1/t2/func to the dict
            bids_dict[subject][session]["t1"] = t1
            bids_dict[subject][session]["t2"] = t2
            bids_dict[subject][session]["func"] = func

    # if combine_sessions enabled, try to fill sessions that are missing an
    # anatomical with another session's anatomical per subject
    if combine_sessions:
        for subject in bids_dict:
            # set default t1/t2
            t1 = list()
            t2 = list()
            # get the first available session with a t1/t2
            for session in bids_dict[subject]:
                if bids_dict[subject][session]["t1"] and bids_dict[subject][session]["t2"]:
                    t1 = bids_dict[subject][session]["t1"]
                    t2 = bids_dict[subject][session]["t2"]
                    break

            # loop over subject sessions, and fill in missing BOTH anatomicals
            for session in bids_dict[subject]:
                if not bids_dict[subject][session]["t1"] and not bids_dict[subject][session]["t2"]:
                    bids_dict[subject][session]["t1"] = t1
                    bids_dict[subject][session]["t2"] = t2

    # make a list of files to run in the form of a tuple (T1, T2, func)
    run_list = list()

    # add subject/session/runs to run_list
    for subject in bids_dict:
        for session in bids_dict[subject]:
            for func in bids_dict[subject][session]["func"]:
                if single_rest_run:
                    # paper only does single rest run
                    if func.entities["task"] == "rest":
                        run_list.append(
                            (bids_dict[subject][session]["t1"][0], bids_dict[subject][session]["t2"][0], func)
                        )
                        break
                else:
                    run_list.append((bids_dict[subject][session]["t1"][0], bids_dict[subject][session]["t2"][0], func))

    # for each item in run_list, run the pipeline.
    for t1, t2, func in run_list:
        # for t1/t2, get subject and session
        t1_subject = t1.entities["subject"]
        t2_subject = t2.entities["subject"]
        t1_session = t1.entities["session"]
        t2_session = t2.entities["session"]
        assert t1_subject == t2_subject
        assert t1_session == t2_session

        # get name of t1 without _T1w.nii.gz suffix
        t1_base = get_prefix(t1.filename).split("_T1w")[0]

        # construct path for anat outputs
        kwargs["anat_path"] = str(
            Path("sub-%s" % t1_subject) / Path("ses-%s" % t1_session) / Path("anat") / Path(t1_base)
        )

        # for functional, get subject and session
        func_subject = func.entities["subject"]
        func_session = func.entities["session"]
        kwargs["subject"] = func_subject
        kwargs["session"] = func_session

        # get name of func without .nii.gz suffix
        func_base = get_prefix(func.filename)

        # construct paths for func/epi outputs
        kwargs["func_path"] = str(
            Path("sub-%s" % func_subject) / Path("ses-%s" % func_session) / Path("func") / Path(func_base)
        )
        kwargs["epi_path"] = kwargs["func_path"]

        # Display files being run.
        logging.info("anat_path: %s", kwargs["anat_path"])
        logging.info("func_path: %s", kwargs["func_path"])
        logging.info("epi_path: %s", kwargs["epi_path"])

        # call function_to_run
        if not dryrun:
            function_to_run(output_path, t1=t1.path, t2=t2.path, func=func.path, metadata=func.get_metadata(), **kwargs)
