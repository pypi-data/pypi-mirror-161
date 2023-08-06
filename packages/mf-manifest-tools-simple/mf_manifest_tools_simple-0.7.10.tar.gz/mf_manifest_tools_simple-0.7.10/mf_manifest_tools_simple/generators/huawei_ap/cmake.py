import os
import shutil
from string import Template

__all__ = ["HuaweiAPCmakeGenerator"]


class HuaweiAPCmakeGenerator(object):

    @staticmethod
    def generate(swc_name: str, output_dir: str, with_conan: bool):
        current_path = os.path.dirname(__file__)

        need_dict = {
            "SWC_NAME": swc_name,
            "swc": swc_name.lower()
        }
        
        if with_conan:
            cmake_template = open(os.path.join(current_path, "cmake_conan.template"), "r").read()

            shutil.copy(os.path.join(current_path, "conanfile.template"), 
                        os.path.join(output_dir, "conanfile.py"))
            shutil.copy(os.path.join(current_path, "mdc_build.template"), 
                        os.path.join(output_dir, "mdc_build.sh"))
        else:
            cmake_template = open(os.path.join(current_path, "cmake.template"), "r").read()

        with open(os.path.join(output_dir, "CMakeLists.txt"), "w") as f:
            f.write(Template(cmake_template).safe_substitute(need_dict))
