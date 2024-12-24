add_plugin(VariancePass)

target_sources(VariancePass PRIVATE
    VariancePass.cpp
    VariancePass.h
    Variance.cs.slang
)
target_copy_shaders(VariancePass RenderPasses/VariancePass)
target_source_group(VariancePass "RenderPasses")
