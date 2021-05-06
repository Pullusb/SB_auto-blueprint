#*-* coding:utf-8 *-*
# ABP -/- Auto-Blueprints V2.9

bl_info = {
    "name": "Auto blueprint",
    "description": "Generate a blueprint scene of the selected object",
    "author": "Samuel Bernou",
    "version": (3, 0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > right-toolbar > Create > auto blueprint",
    "warning": "",
    "wiki_url": "https://github.com/Pullusb/SB_auto-blueprint",
    "category": "Object" }


import bpy
from mathutils import Vector
from math import *

#CONVENIENCE VARIABLES
C = bpy.context
D = bpy.data
O = bpy.ops

#FUNCTIONS

def set_collection(ob, collection, scn=None, unlink=True) :
    ''' link an object in a collection and create it if necessary, if unlink object is removed from other collections'''
    if not scn:
        scn = bpy.context.scene
    col     = None
    visible = False
    linked  = False
 
    # check if collection exist or create it
    for c in bpy.data.collections :
        if c.name == collection : col = c
    if not col : col = bpy.data.collections.new(name=collection)
 
    # link the collection to the scene's collection if necessary
    for c in scn.collection.children :
        if c.name == col.name : visible = True
    if not visible : scn.collection.children.link(col)
 
    # check if the object is already in the collection and link it if necessary
    for o in col.objects :
        if o == ob : linked = True
    if not linked : col.objects.link(ob)
 
    # remove object from scene's collection
    for o in scn.collection.objects :
        if o == ob : scn.collection.objects.unlink(ob)
 
    # if unlink flag we remove the object from other collections
    if unlink :
        for c in ob.users_collection :
            if c.name != collection : c.objects.unlink(ob)


def DuplicateObject(name, copyobj = False, S = False):
    '''Duplicate object with data, link, select and return it'''
    if not S:
        S = bpy.context.scene
    
    if not copyobj:
        copyobj = bpy.context.object
    
    # Create new mesh   
    mesh = bpy.data.meshes.new(name)
 
    # Create new object associated with the mesh
    ob_new = bpy.data.objects.new(name, mesh)
 
    # Copy data block from the old object into the new object
    ob_new.data = copyobj.data.copy()
    ob_new.scale = copyobj.scale
    ob_new.location = copyobj.location
    ob_new.rotation_euler = copyobj.rotation_euler
 
    # Link new object to the given scene and select it
    set_collection(ob_new, "blueprint")
    # S.objects.link(ob_new)
    bpy.ops.object.select_all(action='DESELECT')
    ob_new.select_set(True)
    #how to make it for specific scene dans mother
    #S.objects.active = ob_new
    bpy.context.view_layer.objects.active = ob_new
 
    return ob_new


def SetNewScene(objname):
    '''Create new scene and return source scene'''
    source_scene = bpy.context.scene
    bpy.ops.scene.new(type='NEW') # mode 'EMPTY' to keep settings of previous scene (maybe unstable)
    new = bpy.context.scene
    bpy.context.scene.name = objname
    bpy.context.scene.render.resolution_x = source_scene.render.resolution_x
    bpy.context.scene.render.resolution_y = source_scene.render.resolution_y
    bpy.context.scene.render.resolution_percentage = source_scene.render.resolution_percentage
    return source_scene, new

def SetFreestyleProp(scn, srcScn):
    '''Activate all settings in scene'''
    
    #world settings
    worldName = "BlueprintWorld"
    worldList = [o.name for t, o in bpy.data.worlds.items()]
    
    if not worldList or not worldName in worldList:
        #first Setting of the world
        scn.world = bpy.data.worlds.new(worldName)
        scn.world.color = (0.031985, 0.100398, 0.214036)#set base color (for use in workbench mode)

        scn.world.use_nodes = True
        world_nodes = scn.world.node_tree.nodes
        world_links = scn.world.node_tree.links
        bg = None

        for n in world_nodes:
            if n.type == 'BACKGROUND':
                bg = n

        x,y = bg.location
        n_texcoord = world_nodes.new('ShaderNodeTexCoord')
        n_texcoord.location = (x-1000, y)
        
        n_mapping = world_nodes.new('ShaderNodeMapping')
        n_mapping.inputs['Rotation'].default_value[2] = -1.5708# set rotation to -90
        n_mapping.location = (x-800, y)
        world_links.new(n_texcoord.outputs[5], n_mapping.inputs[0])#6 is windows output

        n_gradient = world_nodes.new('ShaderNodeTexGradient')
        n_gradient.gradient_type = 'EASING'
        n_gradient.location = (x-350, y)
        world_links.new(n_mapping.outputs[0], n_gradient.inputs[0])

        n_mix = world_nodes.new('ShaderNodeMixRGB')
        n_mix.inputs['Color1'].default_value = (0.031985, 0.100398, 0.214036, 1)#horizon_color
        n_mix.inputs['Color2'].default_value = (0.061428, 0.204731, 0.447981, 1)#zenith_color
        n_mix.location = (x-200, y)
        world_links.new(n_gradient.outputs[1], n_mix.inputs[0])
        world_links.new(n_mix.outputs[0], bg.inputs[0])

    else:
        #assign existing world
        scn.world = bpy.data.worlds[worldName]

    #render option
    #'BLENDER_WORKBENCH' is good but only plain color as background and need material to add transparency (need to override materials)

    # scn.render.engine = 'BLENDER_EEVEE' # how to hide object with freestyle On in eevee
    scn.render.engine = 'CYCLES' # disable all object visibility with cycle works
    scn.cycles.samples = 32 #lower value give grainy lines

    scn.render.image_settings.color_mode = 'RGBA' #set output frame to RGBA
    scn.render.use_freestyle = True # activate freestyle for the scene
    scn.render.line_thickness = 1.0

    #renderlayer_options
    scn.view_layers["View Layer"].use_solid = False # Pass to True if object have to be visible
    scn.view_layers["View Layer"].use_halo = False
    scn.view_layers["View Layer"].use_ztransp = False

    if srcScn.ABPenableBG:
        scn.render.film_transparent = False
        scn.view_layers["View Layer"].use_sky = True

    else:
        scn.render.film_transparent = True #set sky as transparent
        scn.view_layers["View Layer"].use_sky = False

    scn.view_layers["View Layer"].use_edge_enhance = False
    scn.view_layers["View Layer"].use_strand = False
    scn.view_layers["View Layer"].use_freestyle = True

    # ols : FS = scn.render.layers['RenderLayer'].freestyle_settings
    FS = bpy.context.view_layer.freestyle_settings
    
    #create linesets
    FS.linesets.new("contour")
    FS.linesets.new("inner")
    FS.linesets.new("backface")
    FS.linesets.new("bluePrintLines_simple")
    FS.linesets.new("bluePrintLines_complex")
    FS.linesets.new("grid")
       
    #base settings
    for l in FS.linesets:
        l.select_border = False
        l.select_silhouette = False
        l.select_crease = False
        l.linestyle.color = (1,1,1)
        l.select_by_collection = True

    FS.crease_angle = radians(162) # after some test, let user define if mesh is organic or hardsurface to have better result
    # line set 1 - contour
    FS.linesets['contour'].select_contour = True
    FS.linesets['contour'].select_external_contour = True
    FS.linesets['contour'].linestyle.thickness = 3.3
    FS.linesets['contour'].collection = bpy.data.collections['frontviews']
    
    # line set 2 - inner
    FS.linesets['inner'].select_crease = True
    FS.linesets['inner'].linestyle.thickness = 2
    FS.linesets['inner'].collection = bpy.data.collections['frontviews']
    if srcScn.ABPdrawEdges: #if user set is owns freestyle mark:
        FS.linesets['inner'].select_edge_mark = True
    
    # line set 3 - backface
    FS.linesets['backface'].select_edge_mark = True
    FS.linesets['backface'].visibility = 'HIDDEN'    
    FS.linesets['backface'].show_render = True # may swith to False when no member in iso collection
    FS.linesets['backface'].linestyle.thickness = 0.8
    FS.linesets['backface'].linestyle.use_dashed_line = True
    FS.linesets['backface'].linestyle.dash1 = 8
    FS.linesets['backface'].linestyle.gap1 = 8
    FS.linesets['backface'].collection = bpy.data.collections['isoviews']

    # line set 4 - bluePrintLines_simple
    FS.linesets['bluePrintLines_simple'].select_contour = True
    FS.linesets['bluePrintLines_simple'].linestyle.thickness = 1
    FS.linesets['bluePrintLines_simple'].linestyle.geometry_modifiers.new('Blueprint', 'BLUEPRINT')
    FS.linesets['bluePrintLines_simple'].linestyle.geometry_modifiers['Blueprint'].shape = 'SQUARES'
    FS.linesets['bluePrintLines_simple'].linestyle.geometry_modifiers['Blueprint'].backbone_length = 35
    FS.linesets['bluePrintLines_simple'].linestyle.geometry_modifiers['Blueprint'].random_backbone = 0
    FS.linesets['bluePrintLines_simple'].collection = bpy.data.collections['blueViews']
    
    # line set 5 - bluePrintLines_complex
    FS.linesets['bluePrintLines_complex'].select_crease = True
    FS.linesets['bluePrintLines_complex'].linestyle.thickness = 0.5
    FS.linesets['bluePrintLines_complex'].linestyle.alpha = 0.8
    FS.linesets['bluePrintLines_complex'].linestyle.geometry_modifiers.new('Blueprint', 'BLUEPRINT')
    FS.linesets['bluePrintLines_complex'].linestyle.geometry_modifiers['Blueprint'].shape = 'SQUARES'
    FS.linesets['bluePrintLines_complex'].linestyle.geometry_modifiers['Blueprint'].backbone_length = 6
    FS.linesets['bluePrintLines_complex'].linestyle.geometry_modifiers['Blueprint'].random_backbone = 1
    FS.linesets['bluePrintLines_complex'].collection = bpy.data.collections['blueViews']
    
    # line set 6 - grid
    FS.linesets['grid'].select_edge_mark = True
    FS.linesets['grid'].linestyle.thickness = 0.4
    FS.linesets['grid'].linestyle.alpha = 0.7
    FS.linesets['grid'].collection = bpy.data.collections['gridViews']
    

def bluename(obj_name):
    '''take a name and return it with "_bp" suffix'''
    return(obj_name + '_bp')
    
def RenameSelected(newname):  
    '''rename selected object (! if nothing is selected: throw an error: index out of range)''' 
    try:
        bpy.context.selected_objects[0].name = newname
    except:
        print ("/!\ try to rename but no object selected")

def FreestyleObject():
    '''Mark all edges as freestyle on selected object'''
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.mark_freestyle_edge(clear=False)
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
def MarkFreestyleEdge(loop=False):
    '''set freestyle line for the object'''
    if loop:
        for i in bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = i
            FreestyleObject()
    else:
        FreestyleObject()


def CheckObject():
    '''check selected objects and make it one if necessary (destructive)'''
    if len(bpy.context.selected_objects) < 1:
        print('select an object to proceed') # info : No object selected
        self.report({'WARNING'}, 'you have to select an object')
        return {'CANCELLED'}

    elif len(bpy.context.selected_objects) == 1:
        obj_name = bluename(bpy.context.selected_objects[0].name)
        #RenameSelected(obj_name)

    elif len(bpy.context.selected_objects) > 1: # if multiple object selected join:
        obj_name = bluename(bpy.context.active_object.name)
        bpy.ops.object.join()
        #RenameSelected(obj_name)

def SetSelectedPivot():
    #bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS') #reset origin to center of mass
    #bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    

def CreateCam(spawn, orthoSize, S):
    '''create and set a camera and attach it to the passed scene'''
    spawn[1] = -200
    bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=(spawn), rotation=(1.5708, 0, 0))
    bpy.context.object.name = "CAM_bp"
    bpy.context.object.data.clip_start = 0.02
    bpy.context.object.data.clip_end = 1000
    bpy.context.object.data.type = 'ORTHO'
    bpy.context.object.data.ortho_scale = orthoSize
    try:
        S.camera = bpy.context.object
    except:
        print ("camera could not be set")
        self.report({'WARNING'}, "cam error")
        return {'CANCELLED'}

def ComputeOrthoSize(LU,RD, X, Z):
    '''Return value of orthographic size'''
    scn = bpy.context.scene
    resX = scn.render.resolution_x
    resY = scn.render.resolution_y
    h = LU[2] + (-RD[2])
    l = (-LU[0]) + RD[0]
    if resX/resY > l/h:
        H = LU[2] + (RD[2] * -1)
        orthoScale = H * (resX/resY)
    else:
        orthoScale = RD[0] + (LU[0] * -1)
    return orthoScale

def selectOnly(OBname):
    bpy.ops.object.select_all(action='DESELECT')
    try:
        sauce = bpy.data.objects.get(OBname)
        sauce.select_set(True)
        bpy.context.view_layer.objects.active = sauce       
    except:
        print("could not select object {}".format(OBname))
    
def Sep(num=20):
    '''print a separator line in console'''
    print (num*"-")

def RenderFrame(S):
    '''Set destination from scene name and render'''
    S.render.filepath = "//Blueprints/" + S.name
    bpy.ops.render.render(animation=False, write_still=True, use_viewport=False, scene= S.name)
    
        
def blueprintIt(scn, srcScn):
    '''Generate blueprint from object'''
    BorderMargin = srcScn.ABPborderMargin #marge

    #select same blueprint values (avoid reset by new scene)
    scn.ABPisOneObject = srcScn.ABPisOneObject
    scn.ABPdrawEdges = srcScn.ABPdrawEdges
    scn.ABPenableBG = srcScn.ABPenableBG
    scn.ABPrenderFinish = srcScn.ABPrenderFinish
    scn.ABPmode = srcScn.ABPmode
    scn.ABPborderMargin = srcScn.ABPborderMargin
    
    ob = bpy.context.object
    ob.rotation_euler = 0,0,0 # reset rotation
    ob.location = scn.cursor.location
    SetSelectedPivot()
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True) # apply scale
    # no need to override materials with a zero-alpha if 'solid' disabled in renderlayer parameter)

    MarkFreestyleEdge()
    X, Y, Z = ob.dimensions # get width, lenght, height
    print("width", X, " lenght", Y, " height", Z)

    originName = bpy.context.object.name

    bpy.context.object.name = originName + "_front"

    blueList = []
    blueList.append(bpy.context.object)
    obCoord = bpy.context.object.location

    gutter = (X + Y) / 4


    if srcScn.ABPmode == "V2A": #"Human2V"
        #transX = X + Y/2 + Y/20
        transX = X/2 + Y/2 + gutter

        blueList.append(DuplicateObject(originName + "_left", bpy.data.objects[originName + "_front"], scn))
        bpy.context.object.rotation_euler.z = 1.5708
        bpy.context.object.location.x = transX

        #find width with left up to right down rectangle:
        lu = Vector([-X/2, 0, Z/2])
        rd = Vector([transX + Y/2, 0, - Z/2])
        
    elif srcScn.ABPmode == "V3A": #"Human3V"
        blueList.append(DuplicateObject(originName + "_quart", bpy.data.objects[originName + "_front"], scn))
        #rotate obj 45 degree
        bpy.context.object.rotation_euler[2] = 0.785398
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        SetSelectedPivot()
        bpy.context.object.location.x = 0
        
        Xtemp = bpy.context.selected_objects[0].dimensions[0]
        
        transX = X/2 + Xtemp/2 + gutter
        bpy.context.object.location.x = transX
        
        transXleft = transX + Xtemp/2 + Y/2 + gutter 
        blueList.append(DuplicateObject(originName + "_left", bpy.data.objects[originName + "_front"], scn))
        bpy.context.object.location.x = transXleft
        
        bpy.context.object.rotation_euler[2] = 1.5708

        #find width with left up to right down rectangle:
        lu = Vector([-X/2, 0, Z/2])
        rd = Vector([transXleft + Y/2, 0, - Z/2])
        #rd = Vector([bpy.context.object.location.x + Y/2, 0, - Z/2])

    elif srcScn.ABPmode == "V4quad": #"Quadview"
        gutter /= 2
        blueList.append(DuplicateObject(originName + "_back", bpy.data.objects[originName + "_front"], scn))
        bpy.context.object.rotation_euler.z = 3.14159
        longest = max(Z,X)
        print("longest", longest)
        transZ = -(longest/2 + Z/2 + gutter)
        bpy.context.object.location.z = transZ

        
        blueList.append(DuplicateObject(originName + "_left", bpy.data.objects[originName + "_front"], scn))
        transX = X/2 + Y/2 + gutter
        bpy.context.object.location.x = transX
        bpy.context.object.rotation_euler[2] = 1.5708

        blueList.append(DuplicateObject(originName + "_top", bpy.data.objects[originName + "_left"], scn))
        bpy.context.object.rotation_euler.y = -1.5708
        bpy.context.object.location.z = transZ
        
        lu = Vector([-X/2, 0, Z/2])
        rd = Vector([bpy.context.object.location.x + Y/2, 0, bpy.context.object.location.z - max(X,Z)/2])

    elif srcScn.ABPmode == "V4show": #"QuadviewShow"
        gutter /= 2
        lu = Vector([-X/2, 0, Z/2])
        
        blueList.append(DuplicateObject(originName + "_iso", bpy.data.objects[originName + "_front"], scn))
        bpy.context.object.rotation_euler = (radians(18.249), radians(-17.387718), radians(42.186459))
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        SetSelectedPivot()
        bpy.context.object.location = (0,0,0)

        tX, tY, tZ = bpy.context.object.dimensions
        mX, mY, mZ = max(tX, X), max(tY,Y), max(tZ,Z)
        print("mX: {} mY: {} mZ: {}".format(mX,mY,mZ))
        
        transZ = -(mZ/2 + Z/2 + gutter)
        transX = mX/2 + max(tX, Y)/2 + gutter
        
        bpy.context.object.location.x = transX
        if tZ <= Z:
            bpy.context.object.location.z = transZ
        else:        
            bpy.context.object.location.z = transZ + (tZ - Z)/2
        
        rd = Vector([bpy.context.object.location.x + max(Y,tX)/2, 0, bpy.context.object.location.z - mZ/2])

        blueList.append(DuplicateObject(originName + "_back", bpy.data.objects[originName + "_front"], scn))
        bpy.context.object.rotation_euler.z = 3.14159
        bpy.context.object.location.z = transZ


        blueList.append(DuplicateObject(originName + "_left", bpy.data.objects[originName + "_front"], scn))
        bpy.context.object.location.x = transX
        bpy.context.object.rotation_euler[2] = 1.5708


    coordLU = obCoord + lu
    coordRD = obCoord + rd
    
    #Set collections
    collectionList = [g.name for g in bpy.data.collections]

    #create collections or link
    if "isoviews" in collectionList:
        isoV = bpy.data.collections['isoviews']
    else:
        isoV = bpy.data.collections.new("isoviews")

    if "frontviews" in collectionList:
        frontV = bpy.data.collections["frontviews"]
    else:
        frontV = bpy.data.collections.new("frontviews")

    if "blueViews" in collectionList:
        blueV = bpy.data.collections["blueViews"]
    else:
        blueV = bpy.data.collections.new("blueViews")
    
    if "gridViews" in collectionList:
        gridV = bpy.data.collections["gridViews"]
    else:
        gridV = bpy.data.collections.new("gridViews")
     
    #consecutive links object to respective group    
    #print (blueList)
    for o in blueList:
        if "_iso" in o.name and o.name not in isoV.objects:
            isoV.objects.link(o)
        if not "BGgrid" in o.name and o.name not in frontV.objects:
            frontV.objects.link(o)
        if not "BGgrid" in o.name and not "_iso" in o.name and o.name not in blueV.objects:
            blueV.objects.link(o)
        if "BGgrid" in o.name and o.name not in gridV.objects:
            gridV.objects.link(o)
        '''
        if not srcScn.ABPkeepObjVisible:
            # disable visibility to keep only line
            # cycle settings
            o.cycles_visibility.camera = False
            o.cycles_visibility.diffuse = False
            o.cycles_visibility.glossy = False
            o.cycles_visibility.shadow = False
            o.cycles_visibility.scatter = False
            o.cycles_visibility.transmission = False
            #override materials with no alpha for eevee or workbench
        '''
    bpy.context.scene.cursor.location = coordLU
    bpy.ops.object.empty_add()
    bpy.context.object.name = "Empty_LeftUp_angle"
    bpy.context.scene.cursor.location = coordRD
    bpy.ops.object.empty_add()
    bpy.context.object.name = "Empty_RightDown_angle"

    #print ("cursorl:", bpy.context.scene.cursor.location)
    print ("coordLU:", coordLU)
    print ("coordRD:", coordRD)

    Sep(5)
        
    coordMidzone = ([(coordLU[0]+ coordRD[0])/2, 0, (coordLU[2]+ coordRD[2])/2])
    bpy.context.scene.cursor.location = coordMidzone

    orthoSize = ComputeOrthoSize(coordLU, coordRD, X, Z)
    orthoSize = orthoSize + (orthoSize * BorderMargin)

    print ("coordMidzone", coordMidzone)
    print ("orthoSize", orthoSize)
    CreateCam(coordMidzone, orthoSize, scn)
    SetFreestyleProp(scn, srcScn)
    
    if srcScn.ABPrenderFinish:
        RenderFrame(scn)
    print('OK')


class ABP_OT_autoBpOps(bpy.types.Operator):
    """Generate Blueprint from selection"""
    bl_idname = "mesh.autobp"
    bl_label = "autoBlueprint Operator"
    bl_options = {'REGISTER'}

    """
    ENUM viewtype :
    Humanoid: [character, human, head]
        2 views aligned: face - side
        3 views aligned: face - 3/4 - side
        4 view aligned: face - 3/4 - side - back
    Object/Vehicle: [voiture, vaisseau]
        4 views : side - face - top - back
        4 views Show : side - face - back - isometric
        all views : side - face - back - side - top - down - isometric
    """

    bpy.types.Scene.ABPmode = bpy.props.EnumProperty(items = [('V2A', '2 aligned', '2 views aligned: face - side'), #[('ENUM1', 'Enum1', 'enum prop 1'),
                                    ('V3A', '3 aligned', '3 views aligned: face - 3/4 - side'),
                                    ('V4quad', '4 two row', '4 views classic : side - face - top - back'),
                                    ('V4show', '4 views show', '4 views Show : side - face - back - isometric')],
                           name="Layout",
                           description="Blueprints layout",
                           default="V4show")

    bpy.types.Scene.ABPisOneObject = bpy.props.BoolProperty(
    name = "Considered as one object",
    description = "all selected considered as one object (else one blueprint per object)",
    default = False
    )
        
    bpy.types.Scene.ABPrenderFinish = bpy.props.BoolProperty(
    name = "Render at finish",
    description = "Render each blueprint",
    default = True
    )
    
    bpy.types.Scene.ABPdrawEdges = bpy.props.BoolProperty(
    name = "Draw all edges",
    description = "Active edgeMark visibility on the full object and all views",
    default = False
    )
    
    bpy.types.Scene.ABPenableBG = bpy.props.BoolProperty(
    name = "Background",
    description = "set a world as background (else transparency)",
    default = True
    )

    """ bpy.types.Scene.ABPkeepObjVisible = bpy.props.BoolProperty(
    name = "Keep object visible",
    description = "let the objects visible under the lines (if unticked, only invisible in cycle for now)",
    default = False
    ) """

    bpy.types.Scene.ABPborderMargin = bpy.props.FloatProperty(
    name = "Border margin",
    description = "Margin between content and border of the frame (default is 0.1)",
    default = 0.1
    )

    #@classmethod
    #def poll(cls, context):
    #    return context.object is not None
    
    def execute(self, context):
        scn = context.scene
        #self.report({'INFO'}, "Blueprints GO")
        objList = [ob for ob in bpy.context.selected_objects if ob.type == 'MESH']
        print(objList)

        #selection check 
        if len(objList) < 1:
            print('select an object to proceed')
            if len(bpy.context.selected_objects) > 0:
                self.report({'WARNING'}, 'you have to select object of type mesh')
            else:
                self.report({'WARNING'}, 'you have to select at least one object')
            return {'CANCELLED'}

        if scn.ABPisOneObject and not bpy.context.active_object:
            self.report({'WARNING'}, "There must be an active object (of type mesh)")
            return {'CANCELLED'}

        for o in bpy.context.selected_objects:
            if o not in objList:
                if bpy.context.active_object == o:
                    errorMsg = o.name + ' is the active object instead of a mesh type object'
                    self.report({'WARNING'}, errorMsg)
                    return {'CANCELLED'}
                else:
                    o.select_set(False)
                
        mainScreen = bpy.context.screen
        srcScn = bpy.context.scene
        StartSceneName = bpy.context.scene.name

        if scn.ABPisOneObject:
            newObList = []    
            newSceneName = bluename(bpy.context.active_object.name)
            print ("current scene 1: ",bpy.context.scene.name)
            srcScene, newScene = SetNewScene(newSceneName)
            print ("current scene 2: ",bpy.context.scene.name)
            for o in objList:
                oN = DuplicateObject(bluename(o.name),o, newScene)
                newObList.append(oN)
        #    mainScreen.scene = bpy.data.scenes[newSceneName]
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.join()
            blueprintIt(newScene, srcScn)
            
        else: #one scene per object
            for o in objList:
                newSceneName = bluename(o.name)
                print ("current scene 12: ",bpy.context.scene.name)
                srcScene, newScene = SetNewScene(newSceneName)
                print ("current scene 22: ",bpy.context.scene.name)
                DuplicateObject(bluename(o.name),o, newScene) # bpy.data.scenes[newSceneName]
                blueprintIt(newScene, srcScn)
        #ENDOFSCRIPT
        self.report({'INFO'}, "Blueprints Done")
        return {'FINISHED'}
    
    #def invoke(self, context, event):
    #    wm.modal_handler_add(self)
    #    return {'RUNNING_MODAL'}  
    #    return wm.invoke_porps_dialog(self)
    #def modal(self, context, event):
    #def draw(self, context):
    
class ABP_PT_autoBpPanel(bpy.types.Panel):
    """Blueprints made easy"""
    bl_idname = "VIEW3D_PT_autobp_panel"
    bl_label = "Auto Blueprints"
    #bl_options =  {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    # bl_context = 'objectmode'
    bl_category = 'Create'
    
    #Panels in ImageEditor are using .poll() instead of bl_context.
    #@classmethod
    #def poll(cls, context):
    #    return context.space_data.show_paint
    
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        col = layout.column()#align=True
        
        col.prop(scn, 'ABPborderMargin')
        col.prop(scn, 'ABPisOneObject')
        col.prop(scn, 'ABPdrawEdges')
        col.prop(scn, 'ABPenableBG')
        # col.prop(scn, 'ABPkeepObjVisible')
        col.prop(scn, 'ABPrenderFinish')
        col.prop(scn, 'ABPmode')
        
        #button
        col = layout.column()
        col.scale_y = 1.5
        col.operator(ABP_OT_autoBpOps.bl_idname, text = "Blueprint selection", icon = 'RENDER_RESULT')


def register():
    bpy.utils.register_class(ABP_OT_autoBpOps)
    bpy.utils.register_class(ABP_PT_autoBpPanel)

def unregister():
    bpy.utils.unregister_class(ABP_OT_autoBpOps)
    bpy.utils.unregister_class(ABP_PT_autoBpPanel)

if __name__ == "__main__":
    register()
