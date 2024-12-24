from falcor import *

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

#m.script('scripts/PathTracer.py')
#m.loadScene('C:/Users/cglab/Downloads/the-breakfast-room/breakfastroom.pyscene', buildFlags=SceneBuilderFlags.Default)
m.script('scripts/PathTracer.py')
#m.script('scripts/OptixDenoiser.py')
#m.script('scripts/SVGF.py')
#m.script('scripts/CaptureMatrices.py')
m.loadScene('C:/Users/cglab/Desktop/YW/scenes/dining-room/dining-room.pyscene', buildFlags=SceneBuilderFlags.Default)

m.frameCapture.outputDir = "C:/Users/cglab/Desktop/YW/result/dining_room/test"
m.clock.framerate = 30
m.clock.time = 0
m.clock.pause()


start = -0.1
end = -0.8
step = -0.005
num_frames = int((end - start) / step)
frame = 0

for y in frange(start, end, step):
    m.clock.frame = frame
    m.scene.lights[0].direction.y = y
    m.renderFrame()
    #for _ in range(4):
    #    m.renderFrame()
    m.frameCapture.baseFilename = f"path_{frame:04d}"
    m.frameCapture.capture()
    frame += 1

exit()






