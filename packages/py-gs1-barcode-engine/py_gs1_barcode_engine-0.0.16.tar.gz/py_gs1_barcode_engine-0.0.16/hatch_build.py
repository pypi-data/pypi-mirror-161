from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import pathlib
import subprocess
import pathlib


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):


        print('doing the things')

        import sys
        import pathlib
        sys.path.append(str(pathlib.Path(__file__).resolve().parent))
        print(sys.path)
        # hacky path hackery
        import compile_and_test_lib
        compile_and_test_lib.execute(pathlib.Path(__file__).resolve().parent / 'build_artifacts')


        print(build_data)
        # {
        #     "infer_tag": False,
        #     "pure_python": True,
        #     "dependencies": [],
        #     "force_include_editable": {},
        #     "artifacts": [],
        #     "force_include": {},
        #     "build_hooks": ("custom",),
        # }
        #

    # def finalize(self, version, build_data, artifact_path):

    #     print(version)
    #     # standard

    #     print(build_data)
    #     # {'infer_tag': False, 'pure_python': True, 'dependencies': [], 'force_include_editable': {}, 'artifacts': [], 'force_include': {}, 'build_hooks': ('custom',)}

    #     print(artifact_path)
    #     # /Users/edward/gs1-playaround/dist/py_gs1_barcode_engine-0.0.8-py3-none-any.whl

    #     print("finalizing")
    #     asdf
