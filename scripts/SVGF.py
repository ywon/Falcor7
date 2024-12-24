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

def render_graph_SVGF():
    g = RenderGraph("SVGF")
    SVGFPass = createPass("SVGFPass", {'Enabled': True, 'Iterations': 4, 'FeedbackTap': 1, 'VarianceEpsilon': 9.999999747378752e-05, 'PhiColor': 10.0, 'PhiNormal': 128.0, 'Alpha': 0.05000000074505806, 'MomentsAlpha': 0.20000000298023224})
    g.addPass(SVGFPass, "SVGFPass")
    GBufferRaster = createPass("GBufferRaster", {'cull': 'Back'})
    g.addPass(GBufferRaster, "GBufferRaster")
    PathTracer = createPass("PathTracer")
    g.addPass(PathTracer, "PathTracer")
    AccumulatePass = createPass("AccumulatePass")
    g.addPass(AccumulatePass, "AccumulatePass")
    add_fileload(g)

    g.addEdge("PathTracer.color", "AccumulatePass.input")
    g.addEdge("FileloadPass.path", "SVGFPass.Color")
    g.addEdge("PathTracer.albedo", "SVGFPass.Albedo")
    g.addEdge("GBufferRaster.vbuffer", "PathTracer.vbuffer")
    g.addEdge("GBufferRaster.diffuseOpacity", "SVGFPass.DiffuseOpacity")
    g.addEdge("GBufferRaster.specRough", "SVGFPass.SpecRough")
    g.addEdge("GBufferRaster.emissive", "SVGFPass.Emission")
    g.addEdge("GBufferRaster.posW", "SVGFPass.WorldPosition")
    g.addEdge("GBufferRaster.guideNormalW", "SVGFPass.WorldNormal")
    g.addEdge("GBufferRaster.pnFwidth", "SVGFPass.PositionNormalFwidth")
    g.addEdge("GBufferRaster.linearZ", "SVGFPass.LinearZ")
    g.addEdge("GBufferRaster.mvec", "SVGFPass.MotionVec")

    #g.markOutput("SVGFPass.Filtered image")
    #g.markOutput("FileloadPass.path")
    g.markOutput("GBufferRaster.diffuseOpacity")

    return g

SVGF = render_graph_SVGF()
try: m.addGraph(SVGF)
except NameError: None
