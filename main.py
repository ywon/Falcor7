from falcor import *

import os

OUT_DIR = "C:/Users/cglab/Desktop/Falcor7/output"

INTERACTIVE = False

NAME = "BistroExterior2"
FILE = "C:/Users/cglab/Desktop/YW/scenes/Bistro_v5_2/BistroExterior.pyscene"
ANIM = [1400, 1410]
METHOD = "ref"
REF_COUNT = 8192
FILELOAD_STARTFRAME = 0

def frange(start, stop=None, step=None):
    # if set start=0.0 and step = 1.0 if not specified
    start = float(start)
    if stop == None:
        stop = start + 0.0
        start = 0.0
    if step == None:
        step = 1.0

    print("start = ", start, "stop = ", stop, "step = ", step)

    count = 0
    while True:
        temp = float(start + count * step)
        if step > 0 and temp >= stop:
            break
        elif step < 0 and temp <= stop:
            break
        yield temp
        count += 1


def add_path(g, gbuf):

    PathTracer = createPass("PathTracer", {'samplesPerPixel': 1})

    path = "PathTracer"

    g.addPass(PathTracer, path)

    g.addEdge(f"{gbuf}.vbuffer", f"{path}.vbuffer")

    return path


def add_gbuffer(g, center=True):

    if center:
        GBufferRaster = createPass("GBufferRaster", {'samplePattern': 'Center', 'sampleCount': 1, 'useAlphaTest': True}) # for input and svgf
    else:
        GBufferRaster = createPass("GBufferRaster", {'samplePattern': 'Stratified', 'sampleCount': 1, 'useAlphaTest': True}) # for input and svgf
    gbuf = "GBufferRaster"
    g.addPass(GBufferRaster, gbuf)
    return gbuf


def add_fileload(g):

    # key:value = filename:channelName
    channels = {
        'path': 'color',
        'albedo': 'albedo',
        'normal': 'normW',
        'mvec': 'mvec',
        'emissive': 'emissive',
        'depth': 'linearZ',
        'position': 'posW',
        'pnFwidth': 'pnFwidth',
    }
    input_dir = f"output/"
    # input_dir = f"./data"
    FileloadPassGbuf = createPass("FileloadPass", {
        'directory': input_dir,
        'filenames': list(channels.keys()),
        'channalNames': list(channels.values()),
        'startFrame': FILELOAD_STARTFRAME,
    })
    gbuffile = "GbufFileloadPass"
    g.addPass(FileloadPassGbuf, gbuffile)

    FileloadPassPath = createPass("FileloadPass", {
        'directory': input_dir,
        'filenames': list(channels.keys()),
        'channalNames': list(channels.values()),
        'startFrame': FILELOAD_STARTFRAME,
    })
    pathfile = "PathFileloadPass"
    g.addPass(FileloadPassPath, pathfile)

    return gbuffile, pathfile


def add_optix(g, gbuffer, path):
    OptixDenoiser = createPass("OptixDenoiser")
    optix = "OptixDenoiser"
    g.addPass(OptixDenoiser, optix)

    g.addEdge(f"{path}.color", f"{optix}.color")
    g.addEdge(f"{path}.albedo", f"{optix}.albedo")
    g.addEdge(f"{gbuffer}.normW", f"{optix}.normal")
    g.addEdge(f"{gbuffer}.mvec", f"{optix}.mvec")

    return optix


def add_svgf(g, gbuffer, path):
    SVGFPass = createPass("SVGFPass", {'Enabled': True, 'Iterations': 4, 'FeedbackTap': 1,
                          'VarianceEpsilon': 1.0e-4, 'PhiColor': 10.0, 'PhiNormal': 128.0, 'Alpha': 0.2, 'MomentsAlpha': 0.2})
    svgf = "SVGFPass"
    g.addPass(SVGFPass, svgf)

    g.addEdge(f"{gbuffer}.emissive", f"{svgf}.Emission")
    g.addEdge(f"{gbuffer}.posW", f"{svgf}.WorldPosition")
    g.addEdge(f"{gbuffer}.normW", f"{svgf}.WorldNormal")
    g.addEdge(f"{gbuffer}.pnFwidth", f"{svgf}.PositionNormalFwidth")
    g.addEdge(f"{gbuffer}.linearZ", f"{svgf}.LinearZ")
    g.addEdge(f"{gbuffer}.mvec", f"{svgf}.MotionVec")
    g.addEdge(f"{path}.color", f"{svgf}.Color")
    g.addEdge(f"{path}.albedo", f"{svgf}.Albedo")

    return svgf


def render_ref(start, end):
    g = RenderGraph("PathGraph")
    # Load libraries

    # Create pass
    GBufferRaster = createPass("GBufferRaster", {'samplePattern': 'Stratified', 'sampleCount': 1, 'useAlphaTest': True})
    PathTracer = createPass("PathTracer", {'samplesPerPixel': 1})
    AccumulatePass = createPass("AccumulatePass", {'enabled': True})
    AccumulatePass3 = createPass("AccumulatePass", {'enabled': True})
    AccumulatePass4 = createPass("AccumulatePass", {'enabled': True})
    AccumulatePass5 = createPass("AccumulatePass", {'enabled': True})

    # Add pass
    g.addPass(GBufferRaster, "GBufferRaster")
    g.addPass(PathTracer, "PathTracer")
    g.addPass(AccumulatePass, "ref_color")
    g.addPass(AccumulatePass3, "ref_envLight")
    g.addPass(AccumulatePass4, "ref_emissive")
    g.addPass(AccumulatePass5, "ref_visibility")

    # Pass G-buffer to path tracer
    g.addEdge("GBufferRaster.vbuffer", "PathTracer.vbuffer")

    # Accumulate
    g.addEdge("PathTracer.color", "ref_color.input")
    g.addEdge("PathTracer.envLight", "ref_envLight.input")
    g.addEdge("GBufferRaster.emissive", "ref_emissive.input")
    g.addEdge("PathTracer.visibility", "ref_visibility.input")

    if not INTERACTIVE:
        outputs = [
            'ref_color.output',
            'ref_envLight.output',
            'ref_emissive.output',
            'ref_visibility.output'
        ]
        for input in outputs:
            g.markOutput(input)

    return g


def render_input(start, end):
    g = RenderGraph("MutlipleGraph")

    gbuf = add_gbuffer(g, center=True)
    path = add_path(g, gbuf)

    if not INTERACTIVE:
        outputs = {
            # PathTracer
            f"{path}.color": TextureChannelFlags.RGB,
            f"{path}.envLight": TextureChannelFlags.RGB,
            f"{path}.visibility": TextureChannelFlags.RGB,
            f"{path}.albedo": TextureChannelFlags.RGB,
            #f"{path}.indirectAlbedo": TextureChannelFlags.RGB,
            f"{path}.reflectionPosW": TextureChannelFlags.RGB,
            f"{path}.specularAlbedo": TextureChannelFlags.RGB,

            #f"{path}.nrdEmission": TextureChannelFlags.RGB,
            f"{path}.nrdDiffuseReflectance": TextureChannelFlags.RGB,
            f"{path}.nrdSpecularReflectance": TextureChannelFlags.RGB,
            f"{path}.nrdDeltaReflectionReflectance": TextureChannelFlags.RGB,
            f"{path}.nrdDeltaReflectionEmission": TextureChannelFlags.RGB,
            # f"{path}.nrdDeltaTransmissionReflectance": TextureChannelFlags.RGB,
            # f"{path}.nrdDeltaTransmissionEmission": TextureChannelFlags.RGB,
            #f"{path}.nrdDeltaTransmissionPosW": TextureChannelFlags.RGB,

            # GBufferRaster
            f"{gbuf}.emissive": TextureChannelFlags.RGB,
            f"{gbuf}.normW": TextureChannelFlags.RGB,
            f"{gbuf}.linearZ": TextureChannelFlags.RGB,
            f"{gbuf}.posW": TextureChannelFlags.RGB,
            f"{gbuf}.mvec": TextureChannelFlags.RGB,
            f"{gbuf}.pnFwidth": TextureChannelFlags.RGB,
            f"{gbuf}.specRough": TextureChannelFlags.RGBA,
            f"{gbuf}.diffuseOpacity": TextureChannelFlags.RGBA,
        }
        for output, flag in outputs.items():
            g.markOutput(output, flag)

    # Add output
    g.markOutput("PathTracer.color")

    return g


def render_svgf_optix(start, end):
    g = RenderGraph("MutlipleGraph")
    # Load libraries

    gbuffile, pathfile = add_fileload(g)

    svgf = add_svgf(g, gbuffile, pathfile)
    optix = add_optix(g, gbuffile, pathfile)

    # Add output
    g.markOutput(f"{optix}.output")
    g.markOutput(f"{svgf}.Filtered image")

    return g


def render_gbufrand(start, end):
    g = RenderGraph("FinalGraph")
    # Load libraries

    gbuf = add_gbuffer(g, False)

    # Create and add capture
    pairs = {
        'emissive2': f'{gbuf}.emissive',
        'normal2': f'{gbuf}.normW',
        'depth2': f'{gbuf}.linearZ',
        'position2': f'{gbuf}.posW',
        'mvec2': f'{gbuf}.mvec',
        'pnFwidth2': f'{gbuf}.pnFwidth',
        'specRough2': f'{gbuf}.specRough',
        'diffuseOpacity2': f'{gbuf}.diffuseOpacity'
    }
    add_capture(g, pairs, start, end)

    return g


def render_PathTracerNRD(start, end):
    g = RenderGraph("PathTracerNRD")


    GBufferRT = createPass("GBufferRT", {'sampleCount': 1, 'useAlphaTest': True})
    g.addPass(GBufferRT, "GBufferRT")
    PathTracer = createPass("PathTracer", {'samplesPerPixel': 1})
    g.addPass(PathTracer, "PathTracer")

    # Reference path passes
    AccumulatePass = createPass("AccumulatePass", {'enabled': True, 'precisionMode': AccumulatePrecision.Single})
    g.addPass(AccumulatePass, "AccumulatePass")
    ToneMapperReference = createPass("ToneMapper", {'autoExposure': False, 'exposureCompensation': 0.0})
    g.addPass(ToneMapperReference, "ToneMapperReference")

    # NRD path passes
    NRDDiffuseSpecular = createPass("NRD", {'maxIntensity': 250.0})
    g.addPass(NRDDiffuseSpecular, "NRDDiffuseSpecular")
    NRDDeltaReflection = createPass("NRD", {'method': NRDMethod.RelaxDiffuse, 'maxIntensity': 250.0, 'worldSpaceMotion': False,
                                            'enableReprojectionTestSkippingWithoutMotion': True, 'spatialVarianceEstimationHistoryThreshold': 1})
    g.addPass(NRDDeltaReflection, "NRDDeltaReflection")
    NRDDeltaTransmission = createPass("NRD", {'method': NRDMethod.RelaxDiffuse, 'maxIntensity': 250.0, 'worldSpaceMotion': False,
                                              'enableReprojectionTestSkippingWithoutMotion': True})
    g.addPass(NRDDeltaTransmission, "NRDDeltaTransmission")
    NRDReflectionMotionVectors = createPass("NRD", {'method': NRDMethod.SpecularReflectionMv, 'worldSpaceMotion': False})
    g.addPass(NRDReflectionMotionVectors, "NRDReflectionMotionVectors")
    NRDTransmissionMotionVectors = createPass("NRD", {'method': NRDMethod.SpecularDeltaMv, 'worldSpaceMotion': False})
    g.addPass(NRDTransmissionMotionVectors, "NRDTransmissionMotionVectors")
    ModulateIllumination = createPass("ModulateIllumination", {'useResidualRadiance': False})
    g.addPass(ModulateIllumination, "ModulateIllumination")

    ToneMapperNRD = createPass("ToneMapper", {'autoExposure': False, 'exposureCompensation': 0.0})
    g.addPass(ToneMapperNRD, "ToneMapperNRD")

    g.addEdge("GBufferRT.vbuffer",                                      "PathTracer.vbuffer")
    g.addEdge("GBufferRT.viewW",                                        "PathTracer.viewW")

    # Reference path graph
    g.addEdge("PathTracer.color",                                       "AccumulatePass.input")
    g.addEdge("AccumulatePass.output",                                  "ToneMapperReference.src")

    # NRD path graph
    g.addEdge("PathTracer.nrdDiffuseRadianceHitDist",                   "NRDDiffuseSpecular.diffuseRadianceHitDist")
    g.addEdge("PathTracer.nrdSpecularRadianceHitDist",                  "NRDDiffuseSpecular.specularRadianceHitDist")
    g.addEdge("GBufferRT.mvecW",                                        "NRDDiffuseSpecular.mvec")
    g.addEdge("GBufferRT.normWRoughnessMaterialID",                     "NRDDiffuseSpecular.normWRoughnessMaterialID")
    g.addEdge("GBufferRT.linearZ",                                      "NRDDiffuseSpecular.viewZ")

    g.addEdge("PathTracer.nrdDeltaReflectionHitDist",                   "NRDReflectionMotionVectors.specularHitDist")
    g.addEdge("GBufferRT.linearZ",                                      "NRDReflectionMotionVectors.viewZ")
    g.addEdge("GBufferRT.normWRoughnessMaterialID",                     "NRDReflectionMotionVectors.normWRoughnessMaterialID")
    g.addEdge("GBufferRT.mvec",                                         "NRDReflectionMotionVectors.mvec")

    g.addEdge("PathTracer.nrdDeltaReflectionRadianceHitDist",           "NRDDeltaReflection.diffuseRadianceHitDist")
    g.addEdge("NRDReflectionMotionVectors.reflectionMvec",              "NRDDeltaReflection.mvec")
    g.addEdge("PathTracer.nrdDeltaReflectionNormWRoughMaterialID",      "NRDDeltaReflection.normWRoughnessMaterialID")
    g.addEdge("PathTracer.nrdDeltaReflectionPathLength",                "NRDDeltaReflection.viewZ")

    g.addEdge("GBufferRT.posW",                                         "NRDTransmissionMotionVectors.deltaPrimaryPosW")
    g.addEdge("PathTracer.nrdDeltaTransmissionPosW",                    "NRDTransmissionMotionVectors.deltaSecondaryPosW")
    g.addEdge("GBufferRT.mvec",                                         "NRDTransmissionMotionVectors.mvec")

    g.addEdge("PathTracer.nrdDeltaTransmissionRadianceHitDist",         "NRDDeltaTransmission.diffuseRadianceHitDist")
    g.addEdge("NRDTransmissionMotionVectors.deltaMvec",                 "NRDDeltaTransmission.mvec")
    g.addEdge("PathTracer.nrdDeltaTransmissionNormWRoughMaterialID",    "NRDDeltaTransmission.normWRoughnessMaterialID")
    g.addEdge("PathTracer.nrdDeltaTransmissionPathLength",              "NRDDeltaTransmission.viewZ")

    g.addEdge("PathTracer.nrdEmission",                                 "ModulateIllumination.emission")
    g.addEdge("PathTracer.nrdDiffuseReflectance",                       "ModulateIllumination.diffuseReflectance")
    g.addEdge("NRDDiffuseSpecular.filteredDiffuseRadianceHitDist",      "ModulateIllumination.diffuseRadiance")
    g.addEdge("PathTracer.nrdSpecularReflectance",                      "ModulateIllumination.specularReflectance")
    g.addEdge("NRDDiffuseSpecular.filteredSpecularRadianceHitDist",     "ModulateIllumination.specularRadiance")
    g.addEdge("PathTracer.nrdDeltaReflectionEmission",                  "ModulateIllumination.deltaReflectionEmission")
    g.addEdge("PathTracer.nrdDeltaReflectionReflectance",               "ModulateIllumination.deltaReflectionReflectance")
    g.addEdge("NRDDeltaReflection.filteredDiffuseRadianceHitDist",      "ModulateIllumination.deltaReflectionRadiance")
    g.addEdge("PathTracer.nrdDeltaTransmissionEmission",                "ModulateIllumination.deltaTransmissionEmission")
    g.addEdge("PathTracer.nrdDeltaTransmissionReflectance",             "ModulateIllumination.deltaTransmissionReflectance")
    g.addEdge("NRDDeltaTransmission.filteredDiffuseRadianceHitDist",    "ModulateIllumination.deltaTransmissionRadiance")
    g.addEdge("PathTracer.nrdResidualRadianceHitDist",                  "ModulateIllumination.residualRadiance")

    # g.addEdge("GBufferRT.mvec",                                         "DLSS.mvec")
    # g.addEdge("GBufferRT.linearZ",                                      "DLSS.depth")
    # g.addEdge("ModulateIllumination.output",                            "DLSS.color")

    g.addEdge("ModulateIllumination.output",                                            "ToneMapperNRD.src")

    # # Outputs
    # g.markOutput("ToneMapperNRD.dst")
    # g.markOutput("ToneMapperReference.dst")

    # Connect input/output
    pairs = {
        # Reproject for ours
        'path': "PathTracer.color",
        'nrd': "ModulateIllumination.output",
        # "emissive": "PathTracer.nrdEmission",
        # 'envLight': "PathTracer.envLight",
        "nrdDiffuseRadianceHitDist": "PathTracer.nrdDiffuseRadianceHitDist",
        "nrdSpecularRadianceHitDist": "PathTracer.nrdSpecularRadianceHitDist",
        # "nrdEmission": "PathTracer.nrdEmission",
        "nrdDiffuseReflectance": "PathTracer.nrdDiffuseReflectance",
        "nrdSpecularReflectance": "PathTracer.nrdSpecularReflectance",
        "nrdDeltaReflectionRadianceHitDist": "PathTracer.nrdDeltaReflectionRadianceHitDist",
        "nrdDeltaReflectionReflectance": "PathTracer.nrdDeltaReflectionReflectance",
        "nrdDeltaReflectionEmission": "PathTracer.nrdDeltaReflectionEmission",
        # "nrdDeltaReflectionNormWRoughMaterialID": "PathTracer.nrdDeltaReflectionNormWRoughMaterialID",
        "nrdDeltaReflectionPathLength": "PathTracer.nrdDeltaReflectionPathLength",
        "nrdDeltaReflectionHitDist": "PathTracer.nrdDeltaReflectionHitDist",
        # "nrdDeltaTransmissionRadianceHitDist": "PathTracer.nrdDeltaTransmissionRadianceHitDist",
        # "nrdDeltaTransmissionReflectance": "PathTracer.nrdDeltaTransmissionReflectance",
        # "nrdDeltaTransmissionEmission": "PathTracer.nrdDeltaTransmissionEmission",
        # "nrdDeltaTransmissionNormWRoughMaterialID": "PathTracer.nrdDeltaTransmissionNormWRoughMaterialID",
        # "nrdDeltaTransmissionPathLength": "PathTracer.nrdDeltaTransmissionPathLength",
        # "nrdDeltaTransmissionPosW": "PathTracer.nrdDeltaTransmissionPosW",
        "nrdResidualRadianceHitDist": "PathTracer.nrdResidualRadianceHitDist",
    }
    opts = {
        'captureCameraMat': False
    }
    add_capture(g, pairs, start, end, opts)

    return g

if 'Dining-room-dynamic-static' == NAME:
    start = -0.5
    end = -0.5
    step = 0
    num_frames = 101
    ANIM = [0, num_frames]
    dir_list = [start] * num_frames
elif 'Dining-room-dynamic' in NAME:
    # Dynamic directional light for dining-room
    # [-0.6, -0.0]
    start = -0.1
    end = -0.8
    target_num_frames = 141
    step = (end - start) / target_num_frames
    dir_list = list(frange(start, end, step))
    num_frames = len(dir_list)
    ANIM = [0, num_frames]

print("ANIM = ", ANIM)

if METHOD == 'input':
    graph = render_input(*ANIM)
elif METHOD == 'ref':
    graph = render_ref(*ANIM)
elif METHOD == 'gbufrand':
    graph = render_gbufrand(*ANIM)
elif METHOD == 'svgf_optix':
    graph = render_svgf_optix(*ANIM)
elif METHOD == 'nrd':
    graph = render_PathTracerNRD(*ANIM)

m.addGraph(graph)
m.loadScene(FILE)
# Call this after scene loading
m.scene.camera.nearPlane = 0.15 # Increase near plane to prevent Z-fighting

m.clock.framerate = 60
m.clock.time = 0

if not INTERACTIVE:
    m.frameCapture.outputDir = OUT_DIR

    # m.profiler.enabled = True
    if 'Dining-room-dynamic' in NAME:
        frame = 0
        for y in dir_list:
            m.clock.frame = frame
            m.scene.lights[0].direction.y = y
            if METHOD == 'ref':
                for _ in range(REF_COUNT):
                    m.renderFrame()
            else:
                m.renderFrame()
            m.frameCapture.baseFilename = f"{frame:04d}"
            m.frameCapture.capture()
            frame += 1
            if frame == ANIM[1] + 1: break
    else:
        # Set start/end frame
        m.clock.frame = ANIM[0]
        m.clock.exitFrame = ANIM[1]
        # Number of frames
        num_frames = ANIM[1] - ANIM[0] + 1

        # frame start from 0 (global clock frame is appended by the Falcor)
        if METHOD == 'ref':
            m.clock.pause()
            for frame in range(num_frames):
                for i in range(REF_COUNT):
                    m.renderFrame()
                m.frameCapture.baseFilename = f"{frame:04d}"
                m.frameCapture.capture()
                m.clock.step()
        else:
            for frame in range(num_frames):
                m.renderFrame()
                m.frameCapture.baseFilename = f"{frame:04d}"
                m.frameCapture.capture()

    # capture = m.profiler.endCapture()
    # m.profiler.enabled = False
    # print(capture)
    # with open('C:/Users/hchoi/repositories/rt-denoiser/event.txt', 'w') as f: f.write(f'{capture}\n')
    exit()
