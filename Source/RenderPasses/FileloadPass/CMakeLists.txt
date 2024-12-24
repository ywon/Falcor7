add_plugin(FileloadPass)

target_sources(FileloadPass PRIVATE
    FileloadPass.cpp
    FileloadPass.h
)

target_source_group(FileloadPass "RenderPasses")
