m.script('scripts/PathTracer.py')
m.loadScene('C:/Users/cglab/Desktop/YW/scenes/Bistro_v5_2/BistroExterior.pyscene', buildFlags=SceneBuilderFlags.Default)
#m.loadScene('C:/Users/cglab/Desktop/YW/BistroExterior_dynamic/BistroExterior_dynamic.pyscene', buildFlags=SceneBuilderFlags.Default)

m.clock.framerate = 30
m.clock.time = 0
#m.clock.pause()
#m.scene.animated = False
#m.clock.exitFrame = 81
m.frameCapture.outputDir = "C:/Users/cglab/Desktop/YW/result/Bistro_exterior"


frame = 0
end = 100
for i in range(end):
    m.clock.frame = i
    m.renderFrame()
    if(frame > 500)
        m.frameCapture.baseFilename = f"path_{frame:04d}"
        m.frameCapture.capture()
    frame += 1
    if(frame==end):
        exit()
