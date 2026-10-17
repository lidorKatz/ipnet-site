"""Reproducible, original architectural scene and scroll-controlled film.

blender -b --python scripts/build-scene.py -- --progress .04 --samples 32
blender -b --python scripts/build-scene.py -- --all --samples 16 --width 960
Blender 4.3+, NumPy and an optional verified OIDN CPU executable are used only
for authoring. No source photographs, client projects or manufacturer models.
"""
from pathlib import Path
import argparse, copy, hashlib, json, math, os, struct, subprocess, sys, time
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "config/journey.json").read_text())
WORK = ROOT / "design/intermediates"
OUTPUT = ROOT / "public/journey"
WORK.mkdir(parents=True, exist_ok=True)
OUTPUT.mkdir(parents=True, exist_ok=True)
START = time.perf_counter()
argsv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
parser = argparse.ArgumentParser()
parser.add_argument("--all", action="store_true")
parser.add_argument("--progress", type=float, default=.04)
parser.add_argument("--width", type=int, default=960)
parser.add_argument("--samples", type=int, default=24)
parser.add_argument("--frames", type=int, default=SPEC["frameCount"])
parser.add_argument("--start", type=int, default=0)
parser.add_argument("--end", type=int)
parser.add_argument("--save-blend", action="store_true")
parser.add_argument("--engine", choices=["CYCLES","BLENDER_EEVEE_NEXT"], default="CYCLES")
parser.add_argument("--oidn", default="/tmp/ipnet-render-tools/oidn-2.5.1.x86_64.linux/bin/oidnDenoise")
ARGS = parser.parse_args(argsv)
if not 0 <= ARGS.progress <= 1 or ARGS.frames < 2:
    raise SystemExit("Invalid progress or frame count")
def P(p): return Vector((p[0], -p[2], p[1]))
def smooth(t):
    t = max(0, min(1, t)); return t*t*(3-2*t)
def portion(p,a,b): return smooth((p-a)/(b-a))
def lerp(a,b,t): return a+(b-a)*t

bpy.ops.wm.read_factory_settings(use_empty=True)
SCENE = bpy.context.scene
def material(name, color, rough=.5, metal=0, transmission=0, emission=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color,1)
    bs.inputs["Roughness"].default_value = rough
    bs.inputs["Metallic"].default_value = metal
    bs.inputs["IOR"].default_value = 1.45
    bs.inputs["Transmission Weight"].default_value = transmission
    if emission:
        bs.inputs["Emission Color"].default_value = (*color,1)
        bs.inputs["Emission Strength"].default_value = emission
    return m
def surface(m, kind):
    n=m.node_tree.nodes; l=m.node_tree.links; bs=n.get("Principled BSDF")
    tc=n.new("ShaderNodeTexCoord")
    noise=n.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value=3
    l.new(tc.outputs["Object"],noise.inputs["Vector"])
    ramp=n.new("ShaderNodeValToRGB")
    if kind=="wood":
        mapping=n.new("ShaderNodeVectorMath"); mapping.operation="MULTIPLY"
        mapping.inputs[1].default_value=(18,18,.7)
        l.new(tc.outputs["Object"],mapping.inputs[0])
        l.new(mapping.outputs["Vector"],noise.inputs["Vector"])
        colors=((.075,.031,.013,1),(.22,.105,.045,1))
        bs.inputs["Roughness"].default_value=.43
    elif kind=="floor":
        colors=((.27,.265,.24,1),(.34,.33,.30,1))
    else:
        colors=((.56,.525,.465,1),(.64,.61,.55,1))
    ramp.color_ramp.elements[0].color=colors[0]
    ramp.color_ramp.elements[1].color=colors[1]
    l.new(noise.outputs["Fac"],ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"],bs.inputs["Base Color"])
    fine=n.new("ShaderNodeTexNoise"); fine.inputs["Scale"].default_value=160 if kind!="wood" else 65
    fine.inputs["Detail"].default_value=2
    l.new(tc.outputs["Object"],fine.inputs["Vector"])
    bump=n.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=.13
    bump.inputs["Distance"].default_value=.003 if kind!="wood" else .0015
    l.new(fine.outputs["Fac"],bump.inputs["Height"]); l.new(bump.outputs["Normal"],bs.inputs["Normal"])
    return m
M={
 "stone":surface(material("Honed warm limestone",(.62,.59,.52),.75),"stone"),
 "floor":surface(material("Honed lobby stone",(.31,.30,.27),.32),"floor"),
 "wood":surface(material("Oiled walnut",(.15,.07,.03),.43),"wood"),
 "dark":material("Dark bronze frame",(.023,.027,.031),.31,.72),
 "black":material("Graphite equipment",(.008,.011,.015),.4,.22),
 "steel":material("Satin stainless steel",(.49,.53,.57),.26,.96),
 "brass":material("Brushed champagne bronze",(.48,.32,.14),.29,.92),
 "glass":material("Clear architectural glazing",(.97,.985,.99),.045,0,1),
 "lens":material("Optical lens",(.018,.032,.055),.075,.15,.65),
 "white":material("Warm white hardware",(.74,.75,.73),.3,.05),
 "fabric":material("Tweed upholstery",(.28,.255,.21),.96),
 "warm":material("Warm diffusers",(1,.72,.40),.5,0,0,3),
 "blue":material("System blue",(.025,.25,.85),.33,.2,0,.7),
 "green":material("Status green",(.12,.52,.30),.35,0,0,.7),
 "road":material("Asphalt",(.035,.042,.052),.88),
 "grout":material("Muted stone joint",(.20,.195,.175),.92),
 "soil":material("Planter soil",(.022,.013,.007),1),
 "leaf":material("Rubber plant leaf",(.035,.085,.025),.48),
}
M["leaf"].node_tree.nodes.get("Principled BSDF").inputs["Subsurface Weight"].default_value=.045
def attach(obj,mat,parent=None):
    if mat: obj.data.materials.append(M[mat] if isinstance(mat,str) else mat)
    SCENE.collection.objects.link(obj)
    if parent: obj.parent=parent
    return obj
def empty(name, at=(0,0,0)):
    obj=bpy.data.objects.new(name,None); SCENE.collection.objects.link(obj); obj.location=P(at); return obj
def box(name,at,size,mat="stone",radius=.006,parent=None,yaw=0):
    x,y,z=size[0]/2,size[2]/2,size[1]/2
    v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    f=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(v,[],f); mesh.update()
    obj=attach(bpy.data.objects.new(name,mesh),mat,parent)
    obj.location=P(at); obj.rotation_euler.z=-yaw
    if radius>0:
        mod=obj.modifiers.new("Physical edge bevel","BEVEL"); mod.width=min(radius,min(size)*.28); mod.segments=3
        mod=obj.modifiers.new("Weighted normals","WEIGHTED_NORMAL"); mod.keep_sharp=True
    return obj
def cylinder(name,at,radius,length,mat="steel",axis=(0,1,0),parent=None,segments=24,radius2=None):
    verts=[]; faces=[]
    for j in range(2):
        r=radius if j==0 or radius2 is None else radius2
        for i in range(segments):
            a=2*math.pi*i/segments; verts.append((r*math.cos(a),r*math.sin(a),(j-.5)*length))
    for i in range(segments):
        nxt=(i+1)%segments; faces.append((i,nxt,nxt+segments,i+segments))
    faces.extend([tuple(range(segments-1,-1,-1)),tuple(range(segments,segments*2))])
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    for poly in mesh.polygons:
        if len(poly.vertices)==4: poly.use_smooth=True
    obj=attach(bpy.data.objects.new(name,mesh),mat,parent); obj.location=P(at)
    obj.rotation_euler=P(axis).to_track_quat("Z","Y").to_euler()
    return obj
def rod(name,start,end,radius,mat="steel",parent=None):
    mid=tuple((a+b)/2 for a,b in zip(start,end)); d=tuple(b-a for a,b in zip(start,end))
    return cylinder(name,mid,radius,Vector(d).length,mat,d,parent,12)
def tube(name,points,radius=.01,mat="steel"):
    data=bpy.data.curves.new(name,"CURVE"); data.dimensions="3D"; data.resolution_u=8
    data.bevel_depth=radius; data.bevel_resolution=2
    spline=data.splines.new("BEZIER"); spline.bezier_points.add(len(points)-1)
    for bp, point in zip(spline.bezier_points,points):
        bp.co=P(point); bp.handle_left_type=bp.handle_right_type="AUTO"
    return attach(bpy.data.objects.new(name,data),mat)
def aim(obj,target): obj.rotation_euler=(P(target)-obj.location).to_track_quat("-Z","Y").to_euler()
def area(name,at,target,power,width,height,color=(1,.79,.55)):
    data=bpy.data.lights.new(name,"AREA"); data.energy=power; data.color=color
    data.shape="RECTANGLE"; data.size=width; data.size_y=height
    obj=bpy.data.objects.new(name,data); SCENE.collection.objects.link(obj); obj.location=P(at); aim(obj,target); return obj
def screen(name,at,size,filepath,parent=None):
    mat=material(name+" display",(.02,.025,.03),.32)
    image=bpy.data.images.load(str(filepath)); n=mat.node_tree.nodes; l=mat.node_tree.links
    tex=n.new("ShaderNodeTexImage"); tex.image=image
    bs=n.get("Principled BSDF"); l.new(tex.outputs["Color"],bs.inputs["Base Color"])
    l.new(tex.outputs["Color"],bs.inputs["Emission Color"]); bs.inputs["Emission Strength"].default_value=.55
    w,h=size[0]/2,size[1]/2
    mesh=bpy.data.meshes.new(name); mesh.from_pydata([(-w,0,-h),(w,0,-h),(w,0,h),(-w,0,h)],[],[(0,1,2,3)])
    uv=mesh.uv_layers.new()
    for loop,xy in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]): loop.uv=xy
    obj=attach(bpy.data.objects.new(name,mesh),mat,parent); obj.location=P(at)
    return obj,tex

# A connected street-level building: front z=6; interior extends toward -z.
box("Street",(0,-.21,21),(100,.14,45),"road",0)
box("Sidewalk",(0,-.045,8),(70,.12,4.1),"floor",.008)
box("Curb",(0,-.12,10.12),(70,.24,.22),"stone",.01)
for x in range(-12,13):
    box("Paving joint",(x*1.2,.017,8),(.002,.001,4),"grout",0)
for z in [6.6,7.8,9]:
    box("Paving joint",(0,.017,z),(50,.001,.002),"grout",0)
box("Lobby floor",(0,-.045,.2),(13.6,.12,12),"floor",.004)
for x in range(-5,6):
    box("Floor joint",(x*1.15,.017,0),(.002,.001,12),"grout",0)
for z in range(-4,5):
    box("Floor joint",(0,.017,z*1.15),(13.6,.001,.002),"grout",0)
box("Lobby ceiling",(0,3.62,0),(13.6,.18,12))
box("West wall",(-6.8,1.8,0),(.23,3.6,12))
box("East wall",(6.8,1.8,0),(.23,3.6,12))
box("Rear wall west",(-2.55,1.8,-5.9),(8.2,3.6,.2))
box("Rear wall east",(5.6,1.8,-5.9),(2.4,3.6,.2))
for x in [-5.5,-2.35,2.35,5.5]:
    box("Entry stone pier",(x,1.8,6),(.8,3.6,.75))
    for y in [.72,1.45,2.18,2.91]:
        box("Stone panel joint",(x,y,6.379),(.79,.002,.002),"grout",0)
box("Entry lintel",(0,3.85,6),(14,.6,.8))
for x in [-3.9,3.9]:
    box("Entry side glazing",(x,1.65,6.08),(2.15,2.95,.028),"glass",0)
    for dx in [-1.1,1.1]:
        box("Glazing frame",(x+dx,1.65,6.1),(.045,3,.09),"dark")
    for y in [.15,1.25,3.14]:
        box("Glazing rail",(x,y,6.1),(2.25,.045,.09),"dark")
box("Canopy",(0,3.5,6.9),(3.7,.12,1.8),"dark",.012)
box("Canopy underside",(0,3.426,6.9),(3.3,.012,1.55),"warm",0)
area("Canopy practical",(0,3.4,6.9),(0,0,6.9),140,3.1,1.3)
for row in range(5):
    y=5.55+row*2.7
    box("Facade spandrel",(0,y-1.23,5.72),(14,.46,.75))
    for col in range(4):
        x=-5.1+col*3.4
        for dx in [-1.58,1.58]:
            box("Facade jamb",(x+dx,y,5.72),(.24,2.47,.75))
        box("Recessed room",(x,y,4.65),(2.85,2.03,.05),"wood" if (row+col)%4==0 else "dark",0)
        box("Upper glazing",(x,y,6.04),(2.88,2.06,.025),"glass",0)
        for dx in [-1.47,0,1.47]:
            box("Window mullion",(x+dx,y,6.07),(.04,2.16,.065),"dark",.003)
        for dy in [-1.07,1.07]:
            box("Window rail",(x,y+dy,6.07),(3,.045,.065),"dark",.003)
        box("Window sill",(x,y-1.11,5.7),(3.07,.09,.85))
        if (row*4+col)%5==0:
            box("Warm upper room",(x-.8,y,4.72),(.3,1.9,.015),"warm",0)
box("Roof cap",(0,18.3,.2),(14.4,.35,12.2))
box("Upper west wall",(-6.95,10.9,0),(.25,14.3,12))
box("Upper east wall",(6.95,10.9,0),(.25,14.3,12))
# Neighbouring architecture also gives the real glazing a reflected streetscape.
for i,x in enumerate([-15,-24,16,25]):
    h=16+(i%3)*3
    box("Neighbouring building",(x,h/2,-1),(7,h,12),"dark",.018)
    for row in range(6):
        for dx in [-1.8,1.8]:
            mat="warm" if (row+i)%4==0 else "glass"
            box("Neighbour window",(x+dx,2+row*2.6,5.04),(1.7,1.8,.035),mat,0)
for x in [-12,-4,4,12,20]:
    box("Opposite street architecture",(x,8.5,35),(7.6,17,8),"stone",.01)
    for y in [3,6,9,12,15]:
        for dx in [-2,0,2]:
            box("Reflected city glazing",(x+dx,y,30.95),(1.3,1.8,.035),"glass",0)

def plant(x,z,seed):
    box("Planter",(x,.29,z),(.88,.58,.85),"dark",.018)
    box("Soil",(x,.58,z),(.81,.025,.77),"soil",.005)
    for i in range(28):
        angle=i*2.39996+seed; radius=.1+(i%7)*.045
        h=.73+(i%6)*.12
        tip=(x+math.cos(angle)*radius,h,z+math.sin(angle)*radius)
        rod("Botanical stem",(x,.58,z),tip,.005,"wood")
        verts=[]; faces=[]
        for j in range(9):
            t=j/8; wid=math.sin(math.pi*t)*.075
            for sign in [-1,1]:
                along=t*.27
                verts.append(P((tip[0]+math.cos(angle)*along+math.sin(angle)*wid*sign,
                                tip[1]+math.sin(math.pi*t)*.035,
                                tip[2]+math.sin(angle)*along-math.cos(angle)*wid*sign)))
        for j in range(8): faces.append((j*2,j*2+1,j*2+3,j*2+2))
        mesh=bpy.data.meshes.new("Curved leaf"); mesh.from_pydata(verts,[],faces)
        for poly in mesh.polygons: poly.use_smooth=True
        attach(bpy.data.objects.new("Botanical leaf",mesh),"leaf")
for i,x in enumerate([-5.5,-3.1,3.1,5.5]): plant(x,7.1,i)

DOORS=[]; CLOSERS=[]
for right in [False,True]:
    pivot=empty("entrance-door-right" if right else "entrance-door-left",(1.04 if right else -1.04,0,6.05))
    sign=-1 if right else 1; c=sign*.515
    box("Door glazing",(c,1.45,0),(.99,2.78,.028),"glass",0,pivot)
    for xx in [0,sign*1.03]:
        box("Door stile",(xx,1.45,.004),(.052,2.9,.07),"dark",.004,pivot)
    for y in [.025,2.88]:
        box("Door rail",(c,y,0),(1.05,.06,.075),"dark",.004,pivot)
    for y in [1.0,1.55]:
        cylinder("Pull mounting boss",(sign*.88,y,.085),.018,.1,"brass",(0,0,1),pivot)
    rod("Brass pull",(sign*.88,1,.14),(sign*.88,1.55,.14),.013,"brass",pivot)
    for y in [.25,1.45,2.65]:
        cylinder("Door hinge",(0,y,.0),.019,.105,"steel",(0,1,0),pivot)
    box("Hydraulic closer body",(c,2.73,-.055),(.25,.065,.07),"steel",.006,pivot)
    DOORS.append((pivot,sign))
box("Threshold",(0,.025,6.05),(2.15,.035,.2),"steel",.002)
for x in [-1.13,1.13]:
    box("Door frame",(x,1.45,6.04),(.07,3,.18),"dark",.004)
box("Door header",(0,2.98,6.04),(2.33,.1,.18),"dark")

# Device screen maps are authored for the demonstration, not live customer feeds.
def prepare_screens():
    # Generate using system Python/Pillow; no runtime fonts or remote images.
    target=WORK/"screens"; target.mkdir(exist_ok=True)
    generator=ROOT/"scripts/make-screens.py"
    subprocess.run(["python3",str(generator),str(target)],check=True)
    return target
SCREEN_DIR=prepare_screens()
box("Intercom mounting",( -1.8,1.65,6.34),(.35,.72,.045),"steel",.012)
box("Video intercom",(-1.8,1.65,6.38),(.31,.68,.06),"black",.013)
for xx in [-.135,.135]:
    for yy in [-.3,.3]: cylinder("Device screw",(-1.8+xx,1.65+yy,6.417),.004,.004,"steel",(0,0,1),segments=10)
cylinder("Intercom camera bezel",(-1.8,1.88,6.425),.03,.01,"steel",(0,0,1))
cylinder("Intercom lens",(-1.8,1.88,6.434),.022,.013,"lens",(0,0,1))
DISPLAY,DISPLAY_TEX=screen("Video intercom UI",(-1.8,1.64,6.414),(.25,.32),SCREEN_DIR/"calling.png")
DISPLAY_IMAGES=[bpy.data.images.load(str(SCREEN_DIR/(key+".png")),check_existing=True) for key in ["calling","connected","granted"]]
cylinder("Intercom call key",(-1.8,1.43,6.425),.025,.009,"steel",(0,0,1))
for y in [1.365,1.373,1.381]: box("Intercom speaker",(-1.8,y,6.414),(.12,.002,.005),"steel",0)
box("Access reader",(1.7,1.5,6.37),(.17,.29,.065),"black",.014)
READER=box("Reader status",(1.7,1.6,6.408),(.09,.009,.004),"blue",.001)
for i in range(3):
    cylinder("Reader contactless arc",(1.7,1.49,6.412),.017+i*.009,.001,"steel",(0,0,1),segments=24)
PHONE=empty("mobile-access-credential",(1.7,1.48,6.8))
box("Mobile credential body",(0,0,0),(.074,.15,.009),"black",.009,PHONE,yaw=-.18)
box("Credential display",(0,0,.005),(.063,.13,.002),"blue",.003,PHONE,yaw=-.18)

def cctv(at):
    x,y,z=at
    box("Camera base",(x,y,z),(.14,.16,.028),"white",.01)
    rod("Camera bracket",(x,y,z+.025),(x,y-.07,z+.19),.025,"white")
    cylinder("Camera body",(x,y-.055,z+.31),.065,.23,"white",(0,-.12,1),segments=32)
    box("Camera sunshield",(x,y+.01,z+.31),(.145,.036,.27),"white",.012)
    cylinder("Lens bezel",(x,y-.07,z+.435),.057,.028,"dark",(0,-.12,1),segments=32)
    cylinder("Optical glass",(x,y-.07,z+.454),.031,.018,"lens",(0,-.12,1),segments=32)
    for i in range(8):
        a=i*math.pi/4
        cylinder("IR emitter",(x+math.cos(a)*.041,y-.07+math.sin(a)*.041,z+.452),.004,.004,"black",(0,0,1),segments=10)
cctv((-3.4,3.05,6.3)); cctv((4.7,3.05,6.3))

# Reception and lounge, with an unobstructed route from entrance to corridor.
box("Reception plinth",(-3.15,.10,-2.1),(3.1,.2,1.03),"dark",.01)
box("Reception walnut",(-3.15,.61,-2.1),(3.12,.96,1.12),"wood",.04)
for i in range(47):
    box("Walnut joinery",(-4.64+i*.064,.61,-1.523),(.036,.84,.045),"wood",.008)
box("Waterfall stone top",(-3.15,1.105,-2.1),(3.38,.11,1.3),"stone",.035)
box("Counter bronze reveal",(-3.15,1.03,-1.49),(3.16,.009,.015),"brass",.002)
box("Monitor stand",(-3.15,1.19,-2.12),(.22,.13,.16),"dark")
box("Security workstation",(-3.15,1.43,-2.12),(.54,.34,.035),"black",.012)
screen("Lobby systems view",(-3.15,1.43,-2.098),(.5,.30),SCREEN_DIR/"monitor.png")
box("Keyboard",(-3.15,1.17,-1.91),(.36,.018,.13),"black",.004)
for i in range(49):
    box("Wall walnut batten",(-4.9+i*.072,1.9,-5.69),(.043,2.62,.13),"wood",.007)
box("Carved stone wall relief",(-3.15,2.03,-5.57),(1.2,.75,.055),"stone",.025)
for y in [1.89,2.03,2.17]:
    tube("Bronze wall relief",[(-3.65,y,-5.532),(-3.3,y+.045,-5.532),(-2.7,y-.015,-5.532)],.005,"brass")
for x in [3.45,5.3]:
    box("Lounge seat",(x,.45,-1.25),(1.05,.25,.90),"fabric",.12)
    box("Lounge curved back",(x,.83,-1.59),(1.05,.64,.25),"fabric",.12)
    for dx in [-.48,.48]:
        box("Lounge arm",(x+dx,.68,-1.25),(.14,.46,.88),"fabric",.065)
    for dx in [-.35,.35]:
        for dz in [-.30,.30]:
            rod("Splayed lounge leg",(x+dx*.85,.37,-1.25+dz*.85),(x+dx,.025,-1.25+dz),.017,"brass")
cylinder("Lounge table base",(4.38,.22,-.4),.19,.43,"dark",segments=32)
cylinder("Lounge table top",(4.38,.455,-.4),.46,.045,"stone",segments=48)
for x in [-4,0,4]:
    box("Recessed light channel",(x,3.512,.35),(.1,.02,7.25),"black",.002)
    box("Lobby light diffuser",(x,3.495,.35),(.034,.012,7.1),"warm",0)
    area("Lobby practical",(x,3.47,.35),(x,0,.35),100,.08,7.0)
area("Reception downlight",(-3.15,3.45,-2.1),(-3.15,.8,-2.1),80,2.6,1.0)
for x in [-6.66,6.66]:
    box("Lobby skirting",(x,.07,0),(.035,.14,11.7),"dark",.003)
plant(-5.2,-3.5,7)

box("Corridor floor",(2.5,-.045,-10),(3.5,.12,8.4),"floor",.003)
box("Corridor ceiling",(2.5,3.62,-10),(3.6,.12,8.4),"stone",.004)
box("Corridor west",( .72,1.8,-10),(.15,3.6,8.4))
XRAYMAT=M["stone"].copy(); XRAYMAT.name="Selective wall reveal"
XRAY=box("xray-corridor-wall",(4.3,1.8,-10),(.15,3.6,8.4),XRAYMAT)
for z in [-7,-10,-13]:
    box("Corridor lighting",(2.5,3.51,z),(1.5,.02,.07),"warm",0)
    area("Corridor practical",(2.5,3.47,z),(2.5,0,z),30,1.5,.08)
box("Network floor",(6.2,-.045,-10.7),(3.6,.12,6.3),"floor")
box("Network side",(8.1,1.8,-10.7),(.15,3.6,6.5))
box("Network rear",(6.2,1.8,-14),(3.8,3.6,.15))
box("Network ceiling",(6.2,3.6,-10.7),(3.8,.15,6.5))
area("Network practical",(6.2,3.35,-10.2),(6.2,.5,-11.2),100,1.8,.45,(.79,.88,1))

RX,RZ=6.25,-11.2
for dx in [-.29,.29]:
    box("Rack cabinet",(RX+dx,1.16,RZ),(.035,2.32,.8),"dark")
for y in [.075,2.30]:
    box("Rack cabinet cap",(RX,y,RZ),(.62,.07,.84),"dark")
box("Rack rear",(RX,1.16,RZ-.39),(.57,2.25,.025),"black",.002)
for dx in [-.2325,.2325]:
    box("Nineteen inch rail",(RX+dx,1.17,RZ+.405),(.022,2.14,.015),"steel",.002)
    for i in range(30):
        box("Rack rail mounting hole",(RX+dx,.22+i*.064,RZ+.415),(.008,.009,.003),"black",0)
for panel,y in enumerate([2.12,1.94,1.73,1.48]):
    box("Patch panel" if panel<2 else "PoE switch",(RX,y,RZ+.27),(.4826,.1 if panel<2 else .13,.26),"black" if panel<2 else "steel",.003)
    for i in range(12):
        x=RX-.207+i*.0376
        box("RJ45 socket",(x,y,RZ+.407),(.026,.024,.019),"black",.002)
        box("Socket contact",(x,y-.005,RZ+.419),(.019,.003,.002),"brass",0)
        if panel>=2:
            box("Port indicator",(x,y+.027,RZ+.412),(.003,.003,.002),"green",0)
    for dx in [-.224,.224]:
        for dy in [-.032,.032]:
            cylinder("Rack screw",(RX+dx,y+dy,RZ+.414),.004,.003,"steel",(0,0,1),segments=10)
for i in range(8):
    x=RX-.18+i*.05
    tube("Dressed patch lead",[(x,2.12,RZ+.427),(x,2.06,RZ+.49),(x,1.82,RZ+.51),(x,1.73,RZ+.429)],.004,"blue" if i%3==0 else "dark")
for name,y,h in [("NVR",.99,.16),("Access controller",.68,.18),("UPS",.28,.27)]:
    box(name,(RX,y,RZ+.14),(.4826,h,.50),"black",.005)
    box(name+" status",(RX+.16,y,RZ+.396),(.035,.024,.004),"blue",.001)
    for j in range(8):
        box(name+" ventilation",(RX-.18+j*.023,y,RZ+.396),(.011,h*.55,.003),"dark",0)
for dx in [-.2,.2]: box("Cable tray rail",(RX+dx,3.2,-9.8),(.02,.04,5.3),"steel",.002)
for i in range(18): box("Cable tray rung",(RX,3.19,-7.3-i*.29),(.42,.012,.025),"steel",.001)

AP=(2.5,3.38,-6.2)
cylinder("Wi-Fi mounting plate",(AP[0],3.51,AP[2]),.145,.035,"steel",segments=40)
cylinder("Wi-Fi access point",AP,.175,.065,"white",segments=48,radius2=.16)
cylinder("Wi-Fi underside",(AP[0],3.335,AP[2]),.145,.035,"white",segments=48,radius2=.12)
box("Wi-Fi indicator",(2.5,3.313,-6.17),(.033,.003,.008),"blue",.002)
CABLES=[]
for name,start in [
    ("CCTV connection",(-3.4,3.05,6.3)),
    ("Intercom connection",(-1.8,1.65,6.3)),
    ("Access connection",(1.7,1.5,6.3)),
    ("Wi-Fi connection",AP)
]:
    route=[start,(start[0],3.1,5.8),(2.5,3.1,3.4),(2.5,3.1,-5.4),(5.6,3.1,-9.7),(RX,2.35,RZ)]
    CABLES.append(tube(name,route,.009,"blue"))

box("Locksmith door",(2.5,1.45,-14.1),(1.35,2.9,.09),"wood",.006)
for x in [1.79,3.21]: box("Locksmith frame",(x,1.5,-14.1),(.065,3,.16),"brass",.003)
box("Locksmith header",(2.5,2.97,-14.1),(1.49,.07,.16),"brass",.003)
box("Door edge shadow gap",(3.18,1.45,-14.04),(.006,2.88,.005),"black",0)
box("Mortise escutcheon",(3.02,1.26,-14.037),(.11,.33,.012),"steel",.015)
for y in [1.13,1.40]: cylinder("Lock plate fastener",(3.02,y,-14.026),.004,.003,"steel",(0,0,1),segments=12)
LEVER=empty("locksmith-lever",(3.02,1.25,-13.997))
cylinder("Lever rose",(0,0,0),.027,.04,"steel",(0,0,1),LEVER,32)
cylinder("Rounded lever",(-.105,0,.035),.015,.18,"steel",(1,0,0),LEVER,24)
CYLINDER=cylinder("locksmith-cylinder",(3.02,1.13,-14.016),.018,.026,"brass",(0,0,1),segments=32)
box("Cylinder keyway",(3.02,1.13,-13.998),(.003,.012,.002),"black",0)
box("Door edge mortise plate",(3.178,1.26,-14.1),(.012,.36,.075),"steel",.002)
LATCH=box("locksmith-latch",(3.192,1.26,-14.1),(.028,.035,.045),"brass",.004)
for x in [0,5]: box("End corridor wall",(x,1.8,-14.22),(3.5,3.6,.15))

# Fixed physical light rig; indirect light and glazing are calculated by Cycles.
world=bpy.data.worlds.new("Blue hour"); world.use_nodes=True; SCENE.world=world
n=world.node_tree.nodes; l=world.node_tree.links
sky=n.new("ShaderNodeTexSky"); sky.sky_type="NISHITA"; sky.sun_elevation=.08; sky.sun_rotation=2.6
sky.altitude=.2; sky.air_density=1.1; sky.dust_density=1.5
background=n.get("Background"); background.inputs["Strength"].default_value=.16
l.new(sky.outputs["Color"],background.inputs["Color"])
area("Large dusk sky",(-8,13,16),(0,2,6),2400,18,14,(.77,.86,1))
area("Street fill",(10,6,13),(0,2,6),250,8,6,(.76,.86,1))

camdata=bpy.data.cameras.new("Journey camera"); CAMERA=bpy.data.objects.new("Journey camera",camdata)
SCENE.collection.objects.link(CAMERA); SCENE.camera=CAMERA
camdata.sensor_fit="VERTICAL"; camdata.sensor_height=24; camdata.clip_start=.025; camdata.clip_end=180
def pose(p):
    way=SPEC["waypoints"]
    i=next((i for i in range(len(way)-1) if way[i]["at"]<=p<=way[i+1]["at"]),len(way)-2)
    a,b=way[i:i+2]; t=portion(p,a["at"],b["at"])
    at=[lerp(x,y,t) for x,y in zip(a["position"],b["position"])]
    target=[lerp(x,y,t) for x,y in zip(a["lookAt"],b["lookAt"])]
    CAMERA.location=P(at); aim(CAMERA,target)
    fov=lerp(a["fov"],b["fov"],t); camdata.lens=24/(2*math.tan(math.radians(fov)/2))
    opening=portion(p,.365,.42)*(1-portion(p,.992,1))
    for door,sign in DOORS: door.rotation_euler.z=sign*opening*math.pi*.47
    PHONE.hide_render=not .325<p<.415
    PHONE.location=P((1.7,1.48,lerp(6.95,6.55,portion(p,.325,.37))))
    status=2 if p>=.285 else 1 if p>=.247 else 0
    DISPLAY_TEX.image=DISPLAY_IMAGES[status]
    bs=XRAYMAT.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Alpha"].default_value=1-.86*portion(p,.55,.64)*(1-portion(p,.94,.97))
    for cable in CABLES: cable.hide_render=not .54<p<.86
    action=math.sin(math.pi*portion(p,.885,.925))
    LEVER.rotation_euler.y=-action*.3
    CYLINDER.rotation_euler.y=-action*.25
    LATCH.location=P((3.192-action*.025,1.26,-14.1))
    return {"progress":p,"position":at,"lookAt":target,"fov":fov,"doorOpening":opening}

SCENE.render.engine=ARGS.engine
if ARGS.engine=="CYCLES":
    SCENE.cycles.device="CPU"; SCENE.cycles.samples=ARGS.samples
    SCENE.cycles.use_adaptive_sampling=True; SCENE.cycles.adaptive_threshold=.045
    SCENE.cycles.max_bounces=8; SCENE.cycles.diffuse_bounces=3
    SCENE.cycles.glossy_bounces=3; SCENE.cycles.transmission_bounces=6
    SCENE.cycles.transparent_max_bounces=6; SCENE.cycles.sample_clamp_indirect=4
    SCENE.cycles.caustics_reflective=False; SCENE.cycles.caustics_refractive=False
    SCENE.cycles.use_denoising=False
    bpy.context.view_layer.cycles.denoising_store_passes=True
SCENE.render.threads_mode="FIXED"; SCENE.render.threads=8
SCENE.render.resolution_x=ARGS.width; SCENE.render.resolution_y=round(ARGS.width*2/3)
SCENE.render.resolution_percentage=100; SCENE.render.use_persistent_data=True
SCENE.view_settings.view_transform="AgX"; SCENE.view_settings.look="AgX - Medium High Contrast"
SCENE.view_settings.exposure=.35
SCENE.render.image_settings.file_format="PNG"; SCENE.render.image_settings.color_mode="RGB"
SCENE.render.image_settings.color_depth="8"

def auxiliary(stem):
    SCENE.use_nodes=True; n=SCENE.node_tree.nodes; n.clear(); l=SCENE.node_tree.links
    source=n.new("CompositorNodeRLayers")
    comp=n.new("CompositorNodeComposite"); l.new(source.outputs["Image"],comp.inputs[0])
    output=n.new("CompositorNodeOutputFile"); output.base_path=str(WORK)
    output.format.file_format="OPEN_EXR"; output.format.color_mode="RGB"; output.format.color_depth="32"; output.format.exr_codec="ZIP"
    output.file_slots.clear()
    paths={}
    for key,port in [("beauty","Image"),("albedo","Denoising Albedo"),("normal","Denoising Normal")]:
        slot=output.file_slots.new(key); slot.path=f"{stem}-{key}-"
        l.new(source.outputs[port],output.inputs[key])
        paths[key]=WORK/f"{stem}-{key}-{SCENE.frame_current:04d}.exr"
    return paths
def pfm(exr,target):
    img=bpy.data.images.load(str(exr),check_existing=False)
    img.colorspace_settings.name="Non-Color"; w,h=img.size
    flat=np.empty(len(img.pixels),np.float32); img.pixels.foreach_get(flat)
    pixels=flat.reshape(h,w,-1)[:,:,:3]
    if not np.isfinite(pixels).all(): raise ValueError("Non-finite render samples")
    if "albedo" in str(exr): pixels=np.clip(pixels,0,1)
    with open(target,"wb") as f:
        f.write(f"PF\n{w} {h}\n-1.0\n".encode()); f.write(pixels.astype("<f4").tobytes())
    bpy.data.images.remove(img)
def read_pfm(file):
    with open(file,"rb") as f:
        assert f.readline().strip()==b"PF"
        w,h=map(int,f.readline().split()); scale=float(f.readline())
        data=np.frombuffer(f.read(),dtype="<f4" if scale<0 else ">f4").copy()
    return data.reshape(h,w,3)
def denoise(paths,stem,target):
    binary=Path(ARGS.oidn)
    if not binary.exists(): raise RuntimeError("Verified OIDN required for clean rendered assets; run scripts/install-render-tools.py")
    expected="1cb3a28ebc99b90d7548b0b8b16f70c163cb59abe8582458a254aa303338269c"
    if hashlib.sha256(binary.read_bytes()).hexdigest()!=expected: raise RuntimeError("OIDN binary checksum mismatch")
    for key,file in paths.items(): pfm(file,WORK/f"{stem}-{key}.pfm")
    env=os.environ.copy(); env["OIDN_DEFAULT_DEVICE"]="CPU"; env["OMP_NUM_THREADS"]="4"
    command=[str(binary),"--device","cpu","--filter","RT","--hdr",str(WORK/f"{stem}-beauty.pfm"),"--alb",str(WORK/f"{stem}-albedo.pfm"),"--nrm",str(WORK/f"{stem}-normal.pfm"),"--output",str(WORK/f"{stem}-denoised.pfm"),"--quality","high","--threads","4"]
    subprocess.run(command,check=True,env=env,stdout=subprocess.DEVNULL)
    rgb=read_pfm(WORK/f"{stem}-denoised.pfm"); h,w,_=rgb.shape
    image=bpy.data.images.new("Clean linear render",width=w,height=h,alpha=True,float_buffer=True)
    rgba=np.ones((h,w,4),np.float32); rgba[:,:,:3]=rgb
    image.colorspace_settings.name="Linear Rec.709"; image.pixels.foreach_set(rgba.ravel())
    image.save_render(str(target),scene=SCENE); bpy.data.images.remove(image)

sourcehash=hashlib.sha256(Path(__file__).read_bytes()+(ROOT/"config/journey.json").read_bytes()).hexdigest()
frames=[]
indices=range(ARGS.start,ARGS.end if ARGS.end is not None else ARGS.frames) if ARGS.all else [0]
for index in indices:
    p=index/(ARGS.frames-1) if ARGS.all else ARGS.progress
    stem=f"frame-{index:03d}" if ARGS.all else "poster"
    target=OUTPUT/"raw"/f"{stem}.png"; target.parent.mkdir(parents=True,exist_ok=True)
    metadata=pose(p); SCENE.frame_set(index+1)
    passes=auxiliary(stem) if ARGS.engine=="CYCLES" else {}
    SCENE.render.filepath=str(WORK/f"{stem}-raw.png")
    if ARGS.save_blend and index==ARGS.start:
        bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(WORK/"building.blend"))
    begin=time.perf_counter(); bpy.ops.render.render(write_still=True)
    if passes: denoise(passes,stem,target)
    else:
        import shutil; shutil.copy2(SCENE.render.filepath,target)
    metadata.update({"seconds":round(time.perf_counter()-begin,2),"samples":ARGS.samples,"engine":ARGS.engine,"sourceSha256":sourcehash,"file":str(target.relative_to(ROOT))})
    (OUTPUT/"raw"/f"{stem}.json").write_text(json.dumps(metadata,indent=2))
    frames.append(metadata)
    print("IPNET_FRAME "+json.dumps(metadata),flush=True)
    # Intermediates are regenerable; retain only the image and provenance per frame.
    for file in WORK.glob(stem+"-*"):
        if file.is_file() and file.suffix in {".exr",".pfm",".png"}: file.unlink()
manifest={"authorship":"Original illustrative 3D property; not a client installation.","sourceSha256":sourcehash,"frameCount":ARGS.frames,"resolution":[SCENE.render.resolution_x,SCENE.render.resolution_y],"frames":frames,"elapsedSeconds":round(time.perf_counter()-START,2)}
(OUTPUT/("render-manifest.json" if ARGS.all else "poster-manifest.json")).write_text(json.dumps(manifest,indent=2))
print("IPNET_RENDER_DONE "+json.dumps({"frames":len(frames),"seconds":manifest["elapsedSeconds"]}),flush=True)
