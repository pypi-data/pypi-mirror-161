"""Functions for image registration.
"""
import os
import signal
import warnings
import tempfile
import multiprocessing as mp
from typing import Tuple
import numpy as np
import nibabel as nib
from scipy.stats import multivariate_normal as mvn
from scipy.stats import beta
from scipy.optimize import least_squares
from scipy.signal.windows import hamming
from omni import io, preprocessing
from omni.resample import resample
from omni.interface import OmniInterface
from omni.interfaces.common import normalize

try:  # try nipy import, but ignore if not available
    from nipy.algorithms.registration.groupwise_registration import SpaceTimeRealign
except ModuleNotFoundError:
    import warnings  # pylint: disable=reimported,ungrouped-imports

    warnings.warn("nipy was not found. Some functions in omni.register may not work.")

# set multiprocessing to spawn due to problematic i/o with fork
try:
    mp.set_start_method("spawn")
except Exception:  # pylint: disable=broad-except
    pass


def grab_slice_encoding_dir(img: nib.Nifti1Image):
    """Grabs the slice encoding direction axis from the Nifti image."""
    try:
        return int(bin(img.header.get("dim_info"))[-6:-4], 2) - 1
    except ValueError:
        print("Could not parse the dim info of the NIFTI file. " "Assuming SED is 2...")
        return 2


def realign4d(
    img: nib.Nifti1Image,  # pylint: disable=dangerous-default-value
    ref_idx: int,
    TR: float,
    slice_times: list,
    slice_encode_dir: int,
    loops: list = [1, 1, 1],
    speedup: list = [5, 3, 1],
    borders: list = [1, 1, 1],
) -> Tuple[np.ndarray, nib.Nifti1Image]:
    """Wrapper for SpaceTimeRealign."""
    # initialize algorithm
    algo = SpaceTimeRealign(img, TR, slice_times, slice_encode_dir)

    # estimates parameters
    print("Initializing estimator...")
    algo.estimate(loops=loops, align_runs=False, speedup=speedup, refscan=ref_idx, borders=borders)

    # get rigid body params (undoes the precond applied to param)
    params = np.array(
        [i.param * i.precond[i.param_inds] for i in algo._transforms[0]]
    )  # pylint: disable=protected-access

    # get resampled image (convert to Nifti1Image)
    # (leave out 4th time axis in affine)
    print("Resampling image...")
    resampled = algo.resample()
    output = nib.Nifti1Image(resampled[0].get_data(), resampled[0].affine[[0, 1, 2, 4]][:, [0, 1, 2, 4]])

    # return rigid body parameters and image output
    return (params, output)


# apply tone curve to outputs
def tone_curve_adj(target: nib.Nifti1Image, synth: nib.Nifti1Image, mask: nib.Nifti1Image = None) -> nib.Nifti1Image:
    print("Running tone curve adjustment...")
    # load target
    target_nm = normalize(target.get_fdata())

    # load params on synth
    def adj_outputs(params):
        return beta.cdf(normalize(synth.get_fdata()), params[0], params[1])

    # mask data
    if mask:
        mask_data = (mask.get_fdata().ravel() > 0) * mask.get_fdata().ravel()
    else:
        mask_data = np.ones(target_nm.ravel().shape)

    # do least squares with bounds
    target_data = target_nm.ravel() * mask_data

    # create optimizable parameter
    def opt_adj_outputs(x):
        return adj_outputs(x).ravel() * mask_data

    # run least squares
    result = least_squares(
        lambda x: target_data - opt_adj_outputs(x),
        (1, 1),
        bounds=([0, 0], [np.inf, np.inf]),
        method="dogbox",
        tr_solver="exact",
        verbose=2,
    )

    # return tone adjusted image
    return nib.Nifti1Image(adj_outputs(result.x), synth.affine, synth.header)


def register_main(
    target,
    interaction,
    source,
    regress_mask=None,
    target_mask=None,
    source_mask=None,
    initial_affine=None,
    output=None,
    regressed_output=None,
    blurred_regressed_output=None,
    aligned_output=None,
    err_tol=1e-4,
    step_size=1e-3,
    max_iterations=200,
    num_params=12,
    optimizer="gd",
    saturate=False,
    equalize=False,
    fixed_regress=False,
    no_register=False,
    output_intmat=False,
    sigma=0,
    bandwidth=0,
    tone_curve=False,
    tone_curve_mask=None,
):
    """Main SynthTarget register routine.

    TODO: This is a mess of a function... Need to clean it up.
    """
    # check if at least one output argument has been defined
    if not any([output, regressed_output, blurred_regressed_output, aligned_output]):
        warnings.warn("No output arguments defined... " "this run will not output any files!")

    # check number of source images (we can only handle up to 10 at the moment)
    if len(source) > 10:
        raise ValueError("Source argument cannot handle more than 10 arguments.")

    # start up interface
    oi = OmniInterface()

    # load/set images
    target_img = nib.load(target)
    oi.set_img("target", target_img)
    # we need to keep alive references to source images for C++ backend
    s_imgs = list()
    s_names = list()  # keep list of source names
    # create tempdir for preprocessing images
    temppath = tempfile.TemporaryDirectory()
    for n, s in enumerate(source):  # read in source images
        print("Loading Image: {}".format(os.path.basename(s)))
        s_img = nib.load(s)  # load image
        if saturate:  # check normalize option
            print("Saturating top/bottom 1% of image voxels...")
            s_img2 = preprocessing.saturate(s_img)
            # we have to save/load image to file, else C++ backend screws up
            s_img2.to_filename(os.path.join(temppath.name, "saturate{}.nii.gz".format(n)))
            s_img = nib.load(os.path.join(temppath.name, "saturate{}.nii.gz".format(n)))
        if equalize:
            print("Equalizing image histogram...")
            s_img2 = preprocessing.equalize(s_img)
            # we have to save/load image to file, else C++ backend screws up
            s_img2.to_filename(os.path.join(temppath.name, "equalize{}.nii.gz".format(n)))
            s_img = nib.load(os.path.join(temppath.name, "equalize{}.nii.gz".format(n)))
        s_imgs.append(s_img)  # store image in array
        s_names.append("source{}".format(n))  # save image name
        oi.set_img("source{}".format(n), s_imgs[-1])  # set image in interface

    # load set masks if availiable
    if target_mask:
        target_mask_img = nib.load(target_mask)
        target_mask_name = "target_mask"
        abs_target_mask_data = np.abs(target_mask_img.get_fdata())
        abs_target_mask_img = nib.Nifti1Image(abs_target_mask_data, target_mask_img.affine, target_mask_img.header)
        oi.set_img(target_mask_name, abs_target_mask_img)
    else:
        target_mask_name = "_NO_MASK_"
    if source_mask:
        source_mask_img = nib.load(source_mask)
        source_mask_name = "source_mask"
        oi.set_img(source_mask_name, source_mask_img)
    else:
        source_mask_name = "_NO_MASK_"
    if regress_mask:
        regress_mask_img = nib.load(regress_mask)
        regress_mask_name = "regress_mask"
        oi.set_img(regress_mask_name, regress_mask_img)
    else:
        regress_mask_name = "_NO_MASK_"

    # load the interaction model
    _, ext = os.path.splitext(interaction)
    if ext == ".model":
        spec = io.load_interaction_spec(interaction)
    else:
        spec = interaction

    # load initial affine if exists, otherwise initialize to identity
    if initial_affine:
        initial_affine = io.read_affine_file(initial_affine)[0]
    else:
        initial_affine = np.eye(4)

    # load fixed regress if exists
    if fixed_regress:
        fixed_regress = np.loadtxt(fixed_regress)
    else:
        fixed_regress = np.array([0])

    # create blurring kernel if specified
    x = np.mgrid[-10:11, -10:11, -10:11].T
    if sigma != 0:
        use_kernel = True
        cov = np.eye(3) * sigma
        kernel = mvn.pdf(x, mean=[0, 0, 0], cov=cov)
    elif bandwidth != 0:
        use_kernel = True

        # define epanechnikov kernel
        def epanechnikov(x, h):
            e = (1 - (1 / h) * (x[:, :, :, 0] ** 2 + x[:, :, :, 1] ** 2 + x[:, :, :, 2] ** 2) > 0) * (
                1 - (1 / h) * (x[:, :, :, 0] ** 2 + x[:, :, :, 1] ** 2 + x[:, :, :, 2] ** 2)
            )
            return e / np.sum(e.ravel())

        # get kernel
        kernel = epanechnikov(x, bandwidth)
    else:
        use_kernel = False
        kernel = None

    # run registration routine
    affine_mat, regress_params = oi.link.registrate(
        "target",
        s_names,
        "regressed",
        "blurred_regressed",
        "aligned",
        spec,
        initial_affine,
        fixed_regress,
        optimizer,
        transcode=num_params,
        target_mask=target_mask_name,
        source_mask=source_mask_name,
        regress_mask=regress_mask_name,
        err_tol=err_tol,
        step_size=step_size,
        iterations=max_iterations,
        no_register=no_register,
        output_intmat=output_intmat,
        use_kernel=use_kernel,
        blur_kernel=kernel,
    )

    # save parameters outputs
    if output:
        print("Writing parameters...")
        # save affine parameters
        io.write_omni_affine(output, affine_mat)
        # save regression parameters
        io.write_regress_params(output, regress_params)

    # get the tone curve mask img
    if tone_curve_mask:
        tone_curve_mask_img = nib.load(tone_curve_mask)
    else:
        tone_curve_mask_img = None

    # get the output
    if regressed_output:
        print("Writing regressed image...")
        regressed_img = oi.get_img("regressed", ref=s_imgs[0])
        regressed_img.to_filename(regressed_output)

    # get the blurred output
    if blurred_regressed_output:
        print("Writing synthetic image...")
        blurred_regressed_img = oi.get_img("blurred_regressed", ref=s_imgs[0])
        blurred_regressed_img.to_filename(blurred_regressed_output)

    # get the aligned image
    if aligned_output:
        print("Writing synthetic target image...")
        aligned_img = oi.get_img("aligned", ref=target_img)
        if tone_curve:  # do tone curve adj if enabled
            if tone_curve_mask_img:
                aligned_tone_curve_mask_img = resample(aligned_img, tone_curve_mask_img, affine_mat)
            else:
                aligned_tone_curve_mask_img = None
            aligned_img = tone_curve_adj(target_img, aligned_img, aligned_tone_curve_mask_img)
        aligned_img.to_filename(aligned_output)

    # clean up temp path
    temppath.cleanup()


def register(*args, **kwargs):
    """There is some kind of memory leak issue in the C++ backend that I can
    not seem to find...

    As a workaround, this just starts the registration routine in a
    separate python process so that it gets cleaned up after it's done.

    This also sends SIGKILL to the job if the user inputs Ctrl+C to the
    main process. TODO: Gracefully handle SIGINT calls
    """
    p = mp.Process(target=register_main, args=args, kwargs=kwargs)
    try:
        p.start()
        p.join()
    except KeyboardInterrupt as e:
        os.kill(p.pid, signal.SIGKILL)
        p.join()
        raise KeyboardInterrupt from e


def phase_corr_translate(target: nib.Nifti1Image, source: nib.Nifti1Image) -> np.ndarray:
    """Does phase correlation to register images (Translation only)."""
    # get data arrays
    target_data = target.get_fdata()
    source_data = source.get_fdata()

    # get resolution
    res = np.abs(target.affine[0, 0])

    # make sure they are the same shape
    assert (
        target_data.shape == source_data.shape
    ), "Target/Source \
        must be same shape!"

    # create hamming window on data
    win_x = hamming(target_data.shape[0])
    win_y = hamming(target_data.shape[1])
    win_z = hamming(target_data.shape[2])
    wins = np.meshgrid(win_x, win_y, win_z, indexing="ij")
    win = np.multiply.reduce(wins)

    # fft them
    target_fft = np.fft.fftn(target_data * win)
    source_fft = np.fft.fftn(source_data * win)
    # to prevent divide by zero errors, set 0 to a very small value
    target_fft[target_fft == 0] = 1e-12
    source_fft[source_fft == 0] = 1e-12

    # take conjugate of the source
    source_fft_conj = np.conj(source_fft)

    # now find the normalized cross correlation
    R = target_fft * source_fft_conj / np.abs(target_fft * source_fft_conj)

    # inverse R
    r = np.real(np.fft.ifftn(R))

    # get translation
    t = np.unravel_index(np.argmax(r), target_data.shape)
    translate = [res * t[0], res * t[1], res * t[2]]

    # get translation in correct FOV
    bound_a = np.dot(target.affine, np.array([0, 0, 0, 1]))
    bound_b = np.dot(target.affine, np.array([target.shape[0] - 1, target.shape[1] - 1, target.shape[2] - 1, 1]))
    ordered_bounds = [np.sort([bound_a[i], bound_b[i]]) for i in range(3)]
    for i in range(3):
        while translate[i] < ordered_bounds[i][0]:
            translate[i] += res * target.shape[i]
        while translate[i] > ordered_bounds[i][1]:
            translate[i] -= res * target.shape[i]

    # return as omni affine
    return np.array([[1, 0, 0, translate[0]], [0, 1, 0, translate[1]], [0, 0, 1, translate[2]], [0, 0, 0, 1]])
