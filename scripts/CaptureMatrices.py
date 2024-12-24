from falcor import *
def add_capture(g):
    OUT_DIR = f"C:/Users/cglab/Desktop/YW/result/kitchen/32spp"

    channels = {
        'path': 'path',
    }

    channels = list(channels.keys())

    options = {
        'directory': OUT_DIR,
        'filenames': channels,
        'channels': channels,
        'exitAtEnd': True,
        'accumulate': True,
        'writeStart': 0,    # Control frame number in below
        'writeEnd': 10000,  # Control frame number in below
        'captureCameraMat': True,
        'includeAlpha': [],
        'startFrame': 0,
    }

    capturepass = "CapturePass"
    CapturePass = createPass("CapturePass", options)
    g.addPass(CapturePass, capturepass)

    return capturepass


def render_graph_capture():
    g = RenderGraph("Capture")

    PathTracer = createPass("PathTracer")
    g.addPass(PathTracer, "PathTracer")
    VBufferRT = createPass("VBufferRT", {'samplePattern': 'Stratified', 'sampleCount': 16, 'useAlphaTest': True})
    g.addPass(VBufferRT, "VBufferRT")
    AccumulatePass = createPass("AccumulatePass")
    g.addPass(AccumulatePass, "AccumulatePass")
    add_capture(g)

    g.addEdge("VBufferRT.vbuffer", "PathTracer.vbuffer")
    g.addEdge("VBufferRT.viewW", "PathTracer.viewW")
    g.addEdge("VBufferRT.mvec", "PathTracer.mvec")
    g.addEdge("PathTracer.color", "AccumulatePass.input")

    #g.markOutput("PathTracer.color")
    g.markOutput("CapturePass.path")

    return g

Capture = render_graph_capture()
try: m.addGraph(Capture)
except NameError: None
