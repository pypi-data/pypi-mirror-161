# TODO(EDWARD): packaging

import ctypes
from pydantic.dataclasses import dataclass
from typing import Optional
from enum import Enum
import pathlib


class Gs1GeneratorError(Exception):
    pass


SHARED_OBJECT_RELATIVE_PATH = "build_artifacts/libgs1encoders.so"
# A. Create library
try:
    c_library = ctypes.CDLL(
        str(
            pathlib.Path(__file__).resolve().parent.parent.parent
            / SHARED_OBJECT_RELATIVE_PATH
        )
    )
except OSError:
    # HACK: the build artifacts are in a different place when packaged in the wheel.
    c_library = ctypes.CDLL(
        str(pathlib.Path(__file__).resolve().parent / SHARED_OBJECT_RELATIVE_PATH)
    )


# define expected arguments and return types

ctx_pointer_type = ctypes.c_void_p  # hack

c_library.gs1_encoder_init.restype = ctx_pointer_type
c_library.gs1_encoder_init.argtypes = []

c_library.gs1_encoder_setFormat.restype = ctypes.c_bool
c_library.gs1_encoder_setFormat.argtypes = [ctx_pointer_type, ctypes.c_int]

c_library.gs1_encoder_setOutFile.restype = ctypes.c_bool
c_library.gs1_encoder_setOutFile.argtypes = [ctx_pointer_type, ctypes.c_char_p]

c_library.gs1_encoder_setSym.restype = ctypes.c_bool
c_library.gs1_encoder_setSym.argtypes = [ctx_pointer_type, ctypes.c_int]

c_library.gs1_encoder_setDataStr.restype = ctypes.c_bool
c_library.gs1_encoder_setDataStr.argtypes = [ctx_pointer_type, ctypes.c_char_p]

c_library.gs1_encoder_setAIdataStr.restype = ctypes.c_bool
c_library.gs1_encoder_setAIdataStr.argtypes = [ctx_pointer_type, ctypes.c_char_p]

c_library.gs1_encoder_setPixMult.restype = ctypes.c_bool
c_library.gs1_encoder_setPixMult.argtypes = [ctx_pointer_type, ctypes.c_int]

c_library.gs1_encoder_setDeviceResolution.restype = ctypes.c_bool
c_library.gs1_encoder_setDeviceResolution.argtypes = [ctx_pointer_type, ctypes.c_double]

c_library.gs1_encoder_setXdimension.restype = ctypes.c_bool
c_library.gs1_encoder_setXdimension.argtypes = [
    ctx_pointer_type,
    ctypes.c_double,
    ctypes.c_double,
    ctypes.c_double,
]

c_library.gs1_encoder_setXundercut.restype = ctypes.c_bool
c_library.gs1_encoder_setXundercut.argtypes = [ctx_pointer_type, ctypes.c_int]

c_library.gs1_encoder_setYundercut.restype = ctypes.c_bool
c_library.gs1_encoder_setYundercut.argtypes = [ctx_pointer_type, ctypes.c_int]

c_library.gs1_encoder_setDmRows.restype = ctypes.c_bool
c_library.gs1_encoder_setDmRows.argtypes = [ctx_pointer_type, ctypes.c_int]

c_library.gs1_encoder_setDmColumns.restype = ctypes.c_bool
c_library.gs1_encoder_setDmColumns.argtypes = [ctx_pointer_type, ctypes.c_int]

c_library.gs1_encoder_encode.restype = ctypes.c_bool
c_library.gs1_encoder_encode.argtypes = [ctx_pointer_type]

c_library.gs1_encoder_getBufferSize.restype = ctypes.c_size_t
c_library.gs1_encoder_getBufferSize.argtypes = [ctx_pointer_type]

c_library.gs1_encoder_copyOutputBuffer.restype = ctypes.c_size_t
c_library.gs1_encoder_copyOutputBuffer.argtypes = [
    ctx_pointer_type,
    ctypes.c_void_p,
    ctypes.c_size_t,
]


c_library.gs1_encoder_getBuffer.restype = ctypes.c_size_t
c_library.gs1_encoder_getBuffer.argtypes = [ctx_pointer_type]

c_library.gs1_encoder_free.argtypes = [ctx_pointer_type]

c_library.gs1_encoder_getErrMsg.restype = ctypes.c_char_p
c_library.gs1_encoder_getErrMsg.argtypes = [ctx_pointer_type]


@dataclass
class ScalingParams:
    @classmethod
    def factory(cls, args: dict):
        if "pix_mult" in args:
            cls = PixelScaling
        else:
            cls = DeviceDotScaling

            args["min_x_dim"] = (
                args["min_x_dim"] if args.get("min_x_dim") is not None else 0
            )
            args["max_x_dim"] = (
                args["max_x_dim"] if args.get("max_x_dim") is not None else 0
            )
        return cls(**args)


@dataclass
class PixelScaling(ScalingParams):
    pix_mult: int


@dataclass
class DeviceDotScaling(ScalingParams):
    resolution: float
    target_x_dim: float
    min_x_dim: Optional[float] = None
    max_x_dim: Optional[float] = None


# TODO read these enums from object file
class Format(Enum):
    gs1_encoder_dBMP = 0
    gs1_encoder_dTIF = 1
    gs1_encoder_dRAW = 2


# TODO read these enums from object file
class Sym(Enum):
    gs1_encoder_sNONE = -1  # < None defined
    gs1_encoder_sDataBarOmni = 0  # < GS1 DataBar Omnidirectional
    gs1_encoder_sDataBarTruncated = 1  # < GS1 DataBar Truncated
    gs1_encoder_sDataBarStacked = 2  # < GS1 DataBar Stacked
    gs1_encoder_sDataBarStackedOmni = 3  # < GS1 DataBar Stacked Omnidirectional
    gs1_encoder_sDataBarLimited = 4  # < GS1 DataBar Limited
    gs1_encoder_sDataBarExpanded = 5  # < GS1 DataBar Expanded (Stacked)
    gs1_encoder_sUPCA = 6  # < UPC-A
    gs1_encoder_sUPCE = 7  # < UPC-E
    gs1_encoder_sEAN13 = 8  # < EAN-13
    gs1_encoder_sEAN8 = 9  # < EAN-8
    gs1_encoder_sGS1_128_CCA = 10  # < GS1-128 with CC-A or CC-B
    gs1_encoder_sGS1_128_CCC = 11  # < GS1-128 with CC-C
    gs1_encoder_sQR = 12  # < (GS1) QR Code
    gs1_encoder_sDM = 13  # < (GS1) Data Matrix
    gs1_encoder_sNUMSYMS = 14  # < Value is the number of symbologies


class Gs1Encoder:
    def __init__(self):
        self._ctx = c_library.gs1_encoder_init(None)

    def setFormat(self, format: Format) -> None:
        result = c_library.gs1_encoder_setFormat(self._ctx, format.value)
        self._handle_error(result)

    def setOutFile(self, out_file: str) -> None:
        result = c_library.gs1_encoder_setOutFile(self._ctx, out_file.encode("ascii"))
        self._handle_error(result)

    def setSym(self, sym: Sym) -> None:
        result = c_library.gs1_encoder_setSym(self._ctx, sym.value)
        self._handle_error(result)

    def setAIdataStr(self, data: str) -> None:
        result = c_library.gs1_encoder_setAIdataStr(self._ctx, data.encode("ascii"))
        self._handle_error(result)

    def setPixMult(self, pix_mult: int) -> None:
        result = c_library.gs1_encoder_setPixMult(self._ctx, pix_mult)
        self._handle_error(result)

    def setDeviceResolution(self, resolution: float) -> None:
        result = c_library.gs1_encoder_setDeviceResolution(self._ctx, resolution)
        self._handle_error(result)

    def setXdimension(self, minimum: float, target: float, maximum: float) -> None:
        result = c_library.gs1_encoder_setXdimension(
            self._ctx, minimum, target, maximum
        )
        self._handle_error(result)

    def setXundercut(self, x_undercut: int) -> None:
        result = c_library.gs1_encoder_setXundercut(self._ctx, x_undercut)
        self._handle_error(result)

    def setYundercut(self, y_undercut: int) -> None:
        result = c_library.gs1_encoder_setYundercut(self._ctx, y_undercut)
        self._handle_error(result)

    def setDmRows(self, dm_rows: int) -> None:
        result = c_library.gs1_encoder_setDmRows(self._ctx, dm_rows)
        self._handle_error(result)

    def setDmColumns(self, dm_cols: int) -> None:
        result = c_library.gs1_encoder_setDmColumns(self._ctx, dm_cols)
        self._handle_error(result)

    def encode(self) -> None:
        result = c_library.gs1_encoder_encode(self._ctx)
        self._handle_error(result)

    def getBufferSize(self) -> int:
        return c_library.gs1_encoder_getBufferSize(self._ctx)

    def getOutputBuffer(self) -> bytes:
        size = self.getBufferSize()
        buffer = ctypes.create_string_buffer(size)
        got_size = c_library.gs1_encoder_copyOutputBuffer(self._ctx, buffer, size)
        if size != got_size:
            raise Gs1GeneratorError("Got buffer of unexpected size")
        return buffer.raw

    def _handle_error(self, last_result: bool):
        if last_result:
            return
        msg = c_library.gs1_encoder_getErrMsg(self._ctx)
        raise Gs1GeneratorError(msg.decode("ascii"))

    def __del__(self):
        c_library.gs1_encoder_free(self._ctx)


OUTPUT_TO_STREAM = ""


def generate_gs1_datamatrix(
    data: str,
    dm_rows: Optional[int] = None,
    dm_cols: Optional[int] = None,
    scaling: Optional[dict] = None,
    x_undercut: Optional[float] = None,
    y_undercut: Optional[float] = None,
) -> bytes:

    """
    Generate a GS1 datamatrix.

    

    :param data: Data to encode in barcode.
    :type data: str
    :param dm_rows: Define the number of rows in the data matrix. \
        If None, then gs1_barcode_engine will choose an appropriate value. \
        See gs1_encoder_getDmRows_. 
    
    :type dm_rows: int or None
    :param dm_cols: Define the number of columns in the data matrix. \
        If None, then gs1_barcode_engine will choose an appropriate value. \
        See gs1_encoder_setDmColumns_. 
    :type dm_cols: int or None
    :param scaling: Scaling parameters to define the size of the generated output. \
        This can be one of two styles. See `Image Scaling Models`_ for more details.

        Pixel scaling
            - No regard for physical dimensions - define module width in units of pixels
            - Use if physical dimensions are not known or are not important
            - Pass a dictionary containing one key ``pix_mult`` with an int value which is the width of a module in units of pixels. \
                e.g. ``{"pix_mult": 5}``.

        Device dot scaling, 
            - Define resolution of target medium and target module dimensions in physical dimensions.
            - Use if resolution of the output medium and target physical size are important.
            - Pass a dictionary with keys ``resolution`` (float) and ``target_x_dim`` (float), and optionally \
                the keys ``min_x_dim`` (float) and ``max_x_dim`` (float). \
                These quantities must be in the same unit of measurement e.g. DPI and inches, otherwise this function may yield unexpected results. \
                e.g. ``{"resolution": 300, "target_x_dim": 0.1}`` 

        The library will attempt to meet these contraints and if these constraints are invalid, \
        py_gs1_barcode_engine.Gs1GeneratorError will be raised.
    :type scaling: dict or None
    :param x_undercut: Compensate for horizontal print growth by shaving this number of pixels from \
        both sides of each module. None is equivalent to 0. See gs1_encoder_setXundercut_.
    :type x_undercut: float or None
    :param y_undercut: Compensate for vertical print growth by shaving this number of pixels from \ 
        both sides of each module. None is equivalent to 0. See gs1_encoder_setYundercut_.
    :type y_undercut: float or None
    
    :raise py_gs1_barcode_engine.Gs1GeneratorError: If the underlying library raises an exception.

    :return: BMP image as bytes
    :rtype: bytes

    .. _gs1_encoder_getDmRows: https://gs1.github.io/gs1-barcode-engine/gs1encoders_8h.html#af9cc3e5dec885cc55aeede3d4163256c
    .. _gs1_encoder_setDmColumns: https://gs1.github.io/gs1-barcode-engine/gs1encoders_8h.html#ac0058e7f2ba0c14bbb1b60dc31d039d2
    .. _gs1_encoder_setXundercut: https://gs1.github.io/gs1-barcode-engine/gs1encoders_8h.html#a290b68be80ac8199ae624af65ecec689
    .. _gs1_encoder_setYundercut: https://gs1.github.io/gs1-barcode-engine/gs1encoders_8h.html#acc6d1ea4f94c108396a759213a7ecfc7
    .. _`Image Scaling Models`: https://gs1.github.io/gs1-barcode-engine/gs1encoders_8h.html#a290b68be80ac8199ae624af65ecec689:~:text=in%20production%20code.-,Image%20scaling%20models,-This%20library%20generates


    """

    if scaling:
        scaling_params = ScalingParams.factory(scaling)
    else:
        scaling_params = None

    gs1 = Gs1Encoder()
    gs1.setFormat(Format.gs1_encoder_dBMP)
    gs1.setOutFile(OUTPUT_TO_STREAM)
    gs1.setSym(Sym.gs1_encoder_sDM)
    gs1.setAIdataStr(data)

    # more configuration

    if isinstance(scaling_params, PixelScaling):
        # 1. Pixel-based scaling system (no real world dimensions)
        gs1.setPixMult(scaling_params.pix_mult)
    elif isinstance(scaling_params, DeviceDotScaling):
        # 2. Device-dot scaling system (real world dimensions)
        gs1.setDeviceResolution(scaling_params.resolution)
        gs1.setXdimension(
            scaling_params.min_x_dim,
            scaling_params.target_x_dim,
            scaling_params.max_x_dim,
        )
    else:
        if scaling_params is None:
            pass
        else:
            assert False

    if x_undercut is not None:
        gs1.setXundercut(x_undercut)

    if y_undercut is not None:
        gs1.setYundercut(y_undercut)

    # Configure datamatrix parameters
    if dm_rows is not None:
        gs1.setDmRows(dm_rows)

    if dm_cols is not None:
        gs1.setDmColumns(dm_cols)

    # Generate output
    gs1.encode()
    return gs1.getOutputBuffer()
