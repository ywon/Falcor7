from falcor import *

def add_fileload(g):
    channels = {
        'path' : 'path',
    }

    input_dir = f"C:/Users/cglab/Desktop/YW/result/emerald_square/32spp"

    FileloadPass = createPass("FileloadPass", {
        'directory': input_dir,
        'filenames': list(channels.keys()),
        'channelNames': list(channels.values()),
        'startFrame': 0,})
    fileload = "FileloadPass"
    g.addPass(FileloadPass, fileload)

    return fileload

def render_graph_OptixDenoiser():
    g = RenderGraph("OptixDenoiser")
    VBufferRT = createPass("VBufferRT")
    g.addPass(VBufferRT, "VBufferRT")
    AccumulatePass = createPass("AccumulatePass")
    g.addPass(AccumulatePass, "AccumulatePass")
    PathTracer = createPass("PathTracer")
    g.addPass(PathTracer, "PathTracer")
    add_fileload(g)
    OptixDenoiser = createPass("OptixDenoiser")
    g.addPass(OptixDenoiser, "OptixDenoiser")
    g.addEdge("VBufferRT.vbuffer", "PathTracer.vbuffer")
    g.addEdge("PathTracer.color", "AccumulatePass.input")
    #g.addEdge("FileloadPass.path", "AccumulatePass.input")
    g.addEdge("FileloadPass.path", "OptixDenoiser.color")
    g.addEdge("PathTracer.albedo", "OptixDenoiser.albedo")
    g.addEdge("PathTracer.guideNormal", "OptixDenoiser.normal")
    g.addEdge("VBufferRT.mvec", "OptixDenoiser.mvec")

    # Color outputs
    g.markOutput("OptixDenoiser.output")
    #g.markOutput("PathTracer.color")
    #g.markOutput("FileloadPass.path")

    # OptixDenoiser inputs
    #g.markOutput("ToneMappingPass.dst")
    #g.markOutput("PathTracer.albedo")
    #g.markOutput("PathTracer.guideNormal")
    #g.markOutput("VBufferRT.mvec")

    return g

OptixDenoiser = render_graph_OptixDenoiser()
try: m.addGraph(OptixDenoiser)
except NameError: None
