#http://blog.codekills.net/2011/07/15/lies,-more-lies-and-python-packaging-documentation-on--package_data-/
from setuptools import Extension, setup, find_packages

setup(
    name="class_7zip_arch",
    version='1.3.2',
    description='Python extension for using 7zip.dll in memory (Example in test/test.py)',
    url='https://github.com/aver007/class_7zip_arch',
    python_requires=">=3.8, <4",
    packages=["class_7zip_arch"],
    package_dir={"class_7zip_arch":"class_7z_arch"},

    include_package_data=True,

    #data_files=[
    package_data={"class_7zip_arch": [
        "*.cpp",
        "*.h",
        "*.dll",
        "libs7z/*.*",
        "libs7z/include/*.*",
        "test/*.*",
        "test/cts/*.*",
    ]},


    ext_modules=[
        Extension(
            name="class_7zip_arch",  # as it would be imported

            sources=[
                "class_7z_arch/_main.cpp",
                "class_7z_arch/Archive.cpp",
                "class_7z_arch/class7zarch.cpp",
                "class_7z_arch/class7zarchiter.cpp",
                "class_7z_arch/misc.cpp"
            ],


            include_dirs = [
                "class_7z_arch/libs7z/include",
            ],
            library_dirs = [
                "class_7z_arch/libs7z",
            ],
            libraries = ["bit7z64",
                         "kernel32",
                         "user32",
                         "gdi32",
                         "winspool",
                         "comdlg32",
                         "advapi32",
                         "shell32",
                         "ole32",
                         "oleaut32",
                         "uuid",
                         "odbc32",
                         "odbccp32",
                         "python38"
            ],

            extra_compile_args =["/MT", "/std:c++17"],
            extra_link_args = [""],
        ),
    ]
)


