import coverage_path_planner as cpp

# Setup environment
# Create perimeter polygon and create environment 
peri = cpp.Polygon([cpp.Point(0,0), cpp.Point(10,0), cpp.Point(10,10), cpp.Point(0,10)])
env = cpp.Environment(peri)

# Add obstacles to environment (optional)
obs = cpp.Polygon([cpp.Point(3, 3), cpp.Point(3, 4), cpp.Point(4, 4)])
env.addObstacle(obs)

# Set virtual wire (optional): valid points for A* calculation. If no virtual wire added A* uses obstacle an perimeter points for search
search_wire = cpp.LineString()
search_wire.addPoint(cpp.Point(1, 1))
search_wire.addPoint(cpp.Point(9, 1))
env.setVirtualWire(search_wire) 

# Add working areas (optional). If no working areas added whole perimeter will be covered
work_area = cpp.Polygon([cpp.Point(2, 2), cpp.Point(2, 6), cpp.Point(8, 6), cpp.Point(8, 2)])
env.addMowArea(work_area)

# Configure settings
settings = cpp.PathSettings()
settings.pattern = "lines"  # possible patterns: lines, squares, rings
settings.offset = 0.18      # distance between coverage lines
settings.angle = 0.5        # coverage angle (RAD)
settings.distanceToBorder = 0.4   # distance to border
settings.mowArea = True       # cover area
settings.mowBorder = True     # calculate border laps (borderLaps must be > 0)
settings.mowBorderCcw = True  # border laps counter clockwise?
settings.borderLaps = 2       # how many border laps (every new lap gets offset of settings.offset)
settings.mowExclusionsBoder = True  # calculate exclusions laps (exclusionsBorderLaps must be > 0)
settings.mowExclusionsBorderCcw = True  # exclusions laps counter clockwise?
settings.exclusionsBorderLaps = 2       # how many exclusions laps (every new lap gets offset of settings.offset)

# Compute path
service = cpp.PathService()
result = service.computeFullTask(env, settings, cpp.Point(5, 5))
print(result.path.getPoints())
