from falcor import *

def render_graph_Variance():
    g = RenderGraph("VarianceAccum")
    GBufferRT = createPass("GBufferRT", {'samplePattern': 'Halton', 'sampleCount': 32, 'useAlphaTest': True})
    g.addPass(GBufferRT, "GBufferRT")
    VBufferRT = createPass("VBufferRT", {'samplePattern': 'Stratified', 'sampleCount': 16, 'useAlphaTest': True})
    g.addPass(VBufferRT, "VBufferRT")
    PathTracer = createPass("PathTracer", {'samplesPerPixel': 1})
    g.addPass(PathTracer, "PathTracer")
    VariancePass = createPass("VariancePass", {'enabled': True, 'precisionMode': 'Single'}) #change to VariancePass
    g.addPass(VariancePass, "VariancePass")

    g.addEdge("VBufferRT.vbuffer", "PathTracer.vbuffer")
    g.addEdge("VBufferRT.viewW", "PathTracer.viewW")
    g.addEdge("VBufferRT.mvec", "PathTracer.mvec")

    g.addEdge("PathTracer.color", "VariancePass.input")
    g.addEdge("GBufferRT.diffuseOpacity", "VariancePass.DiffuseOpacity")
    g.addEdge("GBufferRT.specRough", "VariancePass.SpecRough")

    #g.markOutput("VariancePass.output")
    #g.markOutput("VariancePass.OutMean")
    #g.markOutput("VariancePass.OutVariance")
    #g.markOutput("VariancePass.OutDemodul")
    g.markOutput("VariancePass.OutMoment")
    return g

VarianceAccum = render_graph_Variance()
try: m.addGraph(VarianceAccum)
except NameError: None
