# BlenderIsoRender v0.000001
# Utility for rendering isometric sprites from models
# by solenum (exz) - MIT license
# ##oodnet@libera / oods.net
# ----------------
#
# TODO:
#   - render animation frames
#   - add ui for/handle resolution properly
#   - add ui for/handle lighting/rendering properties

import bpy
import math
import mathutils

class IsoRenderOperator(bpy.types.Operator):
    bl_label = "Iso Render Operator"
    bl_idname = "object.iso_render_operator"
    
    def execute(self, context):
        # set render context
        bpy.context.scene.render.film_transparent = True
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'
        
        # create the camera
        bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 0), rotation=(1.04587, 0.0128535, 2.02015), scale=(1, 1, 1))
        bpy.context.active_object.name = "isoRenderCamera"
        if bpy.context.scene.iso_ortho_cam:
            bpy.data.objects["isoRenderCamera"].data.type = 'ORTHO'
        bpy.data.objects["isoRenderCamera"].select_set(True)
        cam = bpy.context.active_object
        
        # base path for rendered images
        basePath = bpy.context.scene.iso_export_path + "/"
        
        # render each angle
        angleJump = 360.0 / bpy.context.scene.iso_render_angles
        radius = bpy.context.scene.iso_orbit_radius
        height = bpy.context.scene.iso_camera_height
        for i in range(bpy.context.scene.iso_render_angles):
            # calculate the cameras position
            angle = math.radians(i * angleJump)
            dx = radius * math.cos(angle)
            dy = radius * math.sin(angle)
            bpy.context.active_object.location = (dx, dy, height)
            
            # make the camera look at 0,0,0
            direction = bpy.context.active_object.location - mathutils.Vector((0.0, 0.0, 0.0))
            rot = direction.to_track_quat('Z', 'Y').to_matrix().to_4x4()
            loc = mathutils.Matrix.Translation(cam.location)
            cam.matrix_world =  loc @ rot
            
            # render to image
            bpy.context.scene.camera = cam
            bpy.context.scene.render.filepath = basePath + str(i) + ".png" 
            bpy.ops.render.render(use_viewport=False, write_still=True)
        
        # delete lingering camera
        bpy.data.objects["isoRenderCamera"].select_set(True)
        bpy.ops.object.delete()
        
        self.report({'INFO'}, "Done!")
        return {'FINISHED'}

class IsoSpriteRender(bpy.types.Panel):
    bl_label = "Iso Sprite Render"
    bl_idname = "SCENE_PT_Layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
    def draw(self, context):
        layout = self.layout
        
        scene = context.scene
        
        layout.label(text="Settings:")
        
        # export path
        row = layout.row()
        row.prop(scene, "iso_export_path")
        
        row = layout.row()
        row.prop(scene, "iso_render_angles", text="Num Angles")
        row.prop(scene, "iso_angle_offset", text="Angle Offset")
        
        row = layout.row()
        row.prop(scene, "iso_camera_height", text="Cam Height")
        row.prop(scene, "iso_orbit_radius", text="Orbit Radius")
        
        row = layout.row()
        row.prop(scene, "iso_ortho_cam", text="Use Orthographic Camera")
        
        # render button
        layout.label(text="Render")
        row = layout.row()
        row.scale_y = 3.0
        row.operator("object.iso_render_operator", text="Render Sprites")

def register():
    bpy.types.Scene.iso_export_path = bpy.props.StringProperty(
        name = "Iso Export Path",
        subtype = 'DIR_PATH',
        default = bpy.utils.resource_path('USER')
    )
    
    bpy.types.Scene.iso_render_angles = bpy.props.IntProperty(
        name = "Iso Render Angles",
        default = 8
    )
    
    bpy.types.Scene.iso_angle_offset = bpy.props.IntProperty(
        name = "Iso Angle Offset",
        default = 0
    )
    
    bpy.types.Scene.iso_camera_height = bpy.props.IntProperty(
        name = "Iso Camera Height",
        default = 8
    )
    
    bpy.types.Scene.iso_orbit_radius = bpy.props.IntProperty(
        name = "Iso Orbit Radius",
        default = 16
    )
    
    bpy.types.Scene.iso_ortho_cam = bpy.props.BoolProperty(
        name = "Iso Ortho Camera",
        default = False
    )
    
    bpy.utils.register_class(IsoRenderOperator)
    bpy.utils.register_class(IsoSpriteRender)


def unregister():
    del bpy.types.Scene.iso_export_path
    del bpy.types.Scene.iso_render_angles
    del bpy.types.Scene.iso_angle_offset
    del bpy.types.Scene.iso_camera_height
    del bpy.types.Scene.iso_orbit_radius
    del bpy.types.Scene.iso_ortho_cam
    bpy.utils.unregister_class(IsoRenderOperator)
    bpy.utils.unregister_class(IsoSpriteRender)

if __name__ == "__main__":
    register()