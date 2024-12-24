m.script('scripts/PathTracer.py')
m.loadScene('C:/Users/cglab/Desktop/YW/scenes/kitchen/kitchen_animation.pyscene', buildFlags=SceneBuilderFlags.Default)  #Scene path
m.frameCapture.outputDir = "D:/IITP/test"

ref_samples = 1 #sample number for reference
frame_num = 100 #total frame number
m.clock.framerate = 64
m.clock.time = 0
m.clock.exitFrame = frame_num
m.clock.pause()

for i in range(frame_num+1):
    for j in range(ref_samples):
        m. renderFrame()
    m.frameCapture.baseFilename = f"path_{i:04d}"  #edit here for base file name
    m.frameCapture.capture()
    m.clock.step()

exit()


