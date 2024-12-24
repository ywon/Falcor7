GREY_WHITE_ROOM = "D:/scenes/living-room/scene-v4.pbrt"
BEDROOM = "D:/scenes/bedroom/scene-v4.pbrt"
CLASSROOM = "D:/scenes/classroom/scene-v4.pbrt"
SALLE_DE_BAIN = "D:/scenes/bathroom2/scene-v4.pbrt"
SANMIGUEL = "D:/scenes/sanmiguel/sanmiguel-courtyard.pbrt"
BARCELONA_PAVILION = "D:/scenes/barcelona-pavilion/pavilion-day.pbrt"
VILLA = "D:/scenes/villa/villa-lights-on.pbrt"
KROKEN = "D:/scenes/kroken/camera-1.pbrt"
#ZERODAY = "D:/scenes/ZeroDay_v1/MEASURE_ONE/MEASURE_ONE.fbx"
ZERODAY = "D:/scenes/ZeroDay_v1/MEASURE_SEVEN/MEASURE_SEVEN_COLORED_LIGHTS.fbx"
WATERCOLOR = "D:/scenes/watercolor/lights-with-windowglass.pbrt"
VICTORIAN_HOUSE = "D:/scenes/house/scene-v4.pbrt"

m.script('scripts/PathTracer.py')
#m.loadScene(GREY_WHITE_ROOM, buildFlags=SceneBuilderFlags.Default)
m.loadScene(SALLE_DE_BAIN, buildFlags=SceneBuilderFlags.Default)
