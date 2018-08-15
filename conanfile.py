from conans import ConanFile, CMake, tools
from conans.tools import os_info, SystemPackageTool
import os
import shutil


# IMPORTANT NOTE: Even though this is a conan recipe to install VTK, when
# consuming this recipe you should still call find_package for the VTK library
# in order to have the ${VTK_USE_FILE} variable in CMake that you should
# include according with VTK documentation. This is necessary such that vtk
# libraries with factories are properly initialized. Without an
# "INCLUDE(${VTK_USE_FILE})" in your CMakeLists file you will still be able to
# compile and link with VTK, but when running the executable you will get an
# error. Note, however, then you can utill use conan for the
# target_link_libraries as usual in your CMakeLists file.


class vtkConan(ConanFile):
    name = "vtk"
    version = "8.1.1"
    homepage = "https://www.vtk.org/"
    license = "BSD license"
    url = "https://github.com/darcamo/conan-vtk"
    author = "Darlan Cavalcante Moreira (darcamo@gmail.com)"
    description = "The Visualization Toolkit (VTK) is an open-source, \
        freely available software system for 3D computer graphics, \
        image processing, and visualization."
    settings = "os", "compiler", "build_type", "arch"
    # options = {"shared": [True, False]}
    # default_options = "shared=True"
    generators = "cmake"

    def source(self):
        tools.get("https://www.vtk.org/files/release/8.1/VTK-{}.zip".format(
            self.version))
        os.rename("VTK-{}".format(self.version), "sources")
        tools.replace_in_file("sources/CMakeLists.txt",
                              "project(VTK)",
                              """project(VTK)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
SET(CMAKE_INSTALL_RPATH "$ORIGIN")""")

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="lib", src="lib")

    def system_requirements(self):
        if os_info.is_linux:
            installer = SystemPackageTool()
            if os_info.linux_distro == 'arch':
                package_names = ["freeglut", "libxt"]
            else:
                package_names = [
                    "freeglut3-dev", "mesa-common-dev", "mesa-utils-extra",
                    "libgl1-mesa-dev", "libglapi-mesa"]

            for name in package_names:
                installer.install(name)

    def build(self):
        os.mkdir("build")
        shutil.move("conanbuildinfo.cmake", "build/")
        cmake = CMake(self)
        cmake.configure(source_folder="sources", build_folder="build")
        cmake.build()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include/vtk-8.1"]

        self.cpp_info.defines = ["vtkDomainsChemistry_AUTOINIT=1(vtkDomainsChemistryOpenGL2)",
         "vtkIOExport_AUTOINIT=1(vtkIOExportOpenGL2)",
         "vtkRenderingContext2D_AUTOINIT=1(vtkRenderingContextOpenGL2)",
         "vtkRenderingCore_AUTOINIT=3(vtkInteractionStyle,vtkRenderingFreeType,vtkRenderingOpenGL2)",
         "vtkRenderingOpenGL2_AUTOINIT=1(vtkRenderingGL2PSOpenGL2)",
         "vtkRenderingVolume_AUTOINIT=1(vtkRenderingVolumeOpenGL2)"]
