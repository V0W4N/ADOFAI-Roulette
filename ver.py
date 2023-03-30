import pyinstaller_versionfile

pyinstaller_versionfile.create_versionfile_from_input_file(
    output_file="versionfile.txt",
    input_file="info.txt",
    version="1.2.1"
)
