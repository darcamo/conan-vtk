# noqa: D100

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, replace_in_file, collect_libs
from pathlib import Path


class vtkRecipe(ConanFile):  # noqa: D101
    name = "vtk"
    user = "gtel"
    channel = "stable"

    # Optional metadata
    license = "BSD license"
    author = "Darlan Cavalcante Moreira (darcamo@gmail.com)"
    url = "https://github.com/darcamo/conan-vtk"
    description = "The Visualization Toolkit (VTK) is an open-source, \
        freely available software system for 3D computer graphics, \
        image processing, and visualization."
    topics = ("3D", "visualization", "graphics")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False],
               "wrap_python": [True, False]}
    default_options = {"shared": False, "fPIC": True, "wrap_python": False}

    # Sources are located in the same place as this recipe, copy them
    # to the recipe
    exports_sources = "CMakeLists.txt", "src/*", "include/*"

    def source(self):  # noqa: D102
        get(self, self.conan_data['sources'][self.version], strip_root=True)
        # VTK source is missing include for <cinttypes> in some
        # headers, which can results in compile errors (tested with
        # gcc 13)
        replace_in_file(self, Path(self.source_folder) / "ThirdParty/libproj/vtklibproj/src/proj_json_streaming_writer.hpp", "#include <string>", """#include <string>
#include <cinttypes>""")  # noqa: E501
        replace_in_file(self, Path(self.source_folder) / "IO/Image/vtkSEPReader.h", "#include <string> // for std::string", """#include <string> // for std::string
#include <cinttypes>""")  # noqa: E501

    def config_options(self):  # noqa: D102
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):  # noqa: D102
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):  # noqa: D102
        cmake_layout(self)

    def generate(self):  # noqa: D102
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["VTK_WRAP_PYTHON"] = self.options.wrap_python
        tc.generate()

    def build(self):  # noqa: D102
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):  # noqa: D102
        cmake = CMake(self)
        cmake.install()

    def package_info(self):  # noqa: D102
        # NOTE: This will only work for consumers using the CMakeDeps
        # and CMakeToolchain generators. Also, in consumers
        # CMakeLists.txt file they need to link with VTK using
        # something like
        #
        #    target_link_libraries(myexe PRIVATE ${VTK_LIBRARIES})
        #
        # and include the code below after that
        #
        #     include(vtkModule)
        #     # vtk_module_autoinit is needed
        #     vtk_module_autoinit(
        #         TARGETS example
        #         MODULES ${VTK_LIBRARIES}
        #     )
        #
        # This is how VTK is consumed in the VTK examples when it is
        # installed in the system.

        # Tell Conan CMakeDeps generator in the consumers to NOT
        # generate the config files for VTK
        self.cpp_info.set_property("cmake_find_mode", "none")
        # This will add the folder where VTK installed its cmake
        # config files to the CMAKE_PREFIX_PATH variable in the
        # consumer.
        two_digit_version = self.version[:-2]
        assert len(two_digit_version) == 3
        self.cpp_info.builddirs = [f"lib/cmake/vtk-{two_digit_version}"]
