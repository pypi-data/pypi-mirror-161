#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright 2020 Huawei Technologies Co., Ltd
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import acl
import numpy as np


def ptr2array(ptr, shape, dtype, nbytes=0):
    """Convert a ptr buffer to numpy array

    Args:
        ptr (pointer): 
        shape (tuple): Shape of Array to be generate.
        dtype (np.dtype): Array data type.

    Returns:
        array: The generated array with shape 'shape'
    """
    if ptr is None:
        raise ValueError(f"Input ptr should not be None.")

    if not isinstance(shape, tuple):
        raise TypeError(f"Input shape expects a tuple, but got {dtype(shape)}.")

    if not isinstance(dtype, np.dtype):
        raise TypeError(f"Input dtype expects a np.dtype, but got {dtype(dtype)}.")
 
    try:
        array = acl.util.ptr_to_numpy(ptr, shape, dtype)
    except:
        if nbytes != 0:
            _nbytes = nbytes
        else:
            _nbytes = int(np.prod(shape) * dtype.itemsize)
        bytes_data = acl.util.ptr_to_bytes(ptr, _nbytes)
        array = np.frombuffer(bytes_data, dtype=dtype).reshape(shape)

    return array


def array2ptr(array):
    """extract a numpy array's buffer pointer

    Args:
        array(np.ndarray) : Input array

    Returns:
        array_ptr: The buffer's pointer
    """
    if not isinstance(array, np.ndarray):
        raise TypeError(f"Input array expects a np.ndarray, but got {type(array)}.")

    try:
        array_ptr = acl.util.numpy_to_ptr(array)
    except:
        array_ptr = acl.util.bytes_to_ptr(array.tobytes())

    return array_ptr