add_plugin(CapturePass)

target_sources(CapturePass PRIVATE
    CapturePass.cpp
    CapturePass.h
)

target_source_group(CapturePass "RenderPasses")
