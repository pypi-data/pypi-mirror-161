from setuptools import setup, Extension
import pybind11

setup(
    packages = ["jax_triton"],
    ext_modules = [
      Extension(
        name="jax_triton.custom_call",
        sources=["lib/custom_call.cc"],
        include_dirs = [
          "/usr/local/cuda/include",
          pybind11.get_include()], 
        libraries = ["cuda"],
        library_dirs = ["/usr/local/cuda/lib64", "/usr/local/cuda/lib64/stubs"],
        )])
