cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(VTK COMPONENTS
  CommonColor
  CommonCore
  FiltersSources
  InteractionStyle
  RenderingContextOpenGL2
  RenderingCore
  RenderingFreeType
  RenderingGL2PSOpenGL2
  RenderingOpenGL2
)

if (NOT VTK_FOUND)
  message(FATAL_ERROR "CylinderExample: Unable to find the VTK build folder.")
endif()

add_executable(example src/example.cpp)
target_link_libraries(example PRIVATE ${VTK_LIBRARIES})

include(vtkModule)
# vtk_module_autoinit is needed
vtk_module_autoinit(
  TARGETS example
  MODULES ${VTK_LIBRARIES}
)
