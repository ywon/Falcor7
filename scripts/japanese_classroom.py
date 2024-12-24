m.script('scripts/PathTracer.py')
m.loadScene('D:/scenes/breakfastroom/breakfastroom.pyscene', buildFlags=SceneBuilderFlags.Default)

#m.renderFrame()

m.clock.framerate = 30
m.clock.time = 0
m.clock.pause()

m.frameCapture.outputDir = "C:/Users/cglab/Desktop/YW/result/breakfast_room"

frame = 0
end = 20
for i in range(0, end):
    m.clock.frame = i
    m.renderFrame()
    m.frameCapture.baseFilename = f"path_{frame:04d}"
    m.frameCapture.capture()
    frame += 1
    if(frame==end):
        exit()

