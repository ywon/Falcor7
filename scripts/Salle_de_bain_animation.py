#m.script('scripts/SVGF.py')
#m.script('scripts/OptixDenoiser.py')
#m.script('scripts/CaptureMatrices.py')
m.script('scripts/PathTracer.py')
m.loadScene('D:/scene_file/EmeraldSquare_v4_1/EmeraldSquare_v4_1/EmeraldSquare_Day.pyscene', buildFlags=SceneBuilderFlags.Default)
m.frameCapture.outputDir = "C:/Users/cglab/Desktop/YW/result/emerald_square"


m.clock.framerate = 30
m.clock.time = 0
m.clock.pause()

frame = 0
end = 500

for i in range(end):
    m.clock.frame = i
    m.renderFrame()
    #if(frame > 500):
    m.frameCapture.baseFilename = f"spec_{frame:04d}"
    m.frameCapture.capture()
    frame += 1
    if(frame == end):
        exit()

