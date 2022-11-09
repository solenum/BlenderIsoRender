# BlenderIsoRender v0.000001
# Utility for rendering isometric sprites from models
# by solenum (exz) - MIT license
# ##oodnet@libera / oods.net
# ----------------

import bpy
import math
import mathutils

class IsoRenderOperator(bpy.types.Operator):
    bl_label = "Iso Render Operator"
    bl_idname = "object.iso_render_operator"
    
    def execute(self, context):
        # store reference to selected object
        obj = bpy.context.active_object
        
        if not obj:
            self.report({'INFO'}, "No selected armature or object!")
            return {'FINISHED'}
        
        if not bpy.context.scene.iso_render_static:
            if not obj.animation_data or not obj.animation_data.nla_tracks or len(obj.animation_data.nla_tracks) == 0:
                self.report({'INFO'}, "Selected armature contains no actions!")
                return {'FINISHED'}
        
        # list of animations to export
        exportAnims = bpy.context.scene.iso_action_names.split(',')     
        
        # set render context
        bpy.context.scene.render.film_transparent = True
        bpy.context.scene.render.image_settings.color_mode = 'RGBA'
        bpy.context.scene.render.resolution_x = bpy.context.scene.iso_render_x
        bpy.context.scene.render.resolution_y = bpy.context.scene.iso_render_y
        bpy.context.scene.render.resolution_percentage = 100
        bpy.context.scene.render.filter_size = bpy.context.scene.iso_filter_size
        bpy.context.scene.render.use_border = False
        
        # create the camera
        bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 0), rotation=(1.04587, 0.0128535, 2.02015), scale=(1, 1, 1))
        bpy.context.active_object.name = "isoRenderCamera"
        if bpy.context.scene.iso_ortho_cam:
            bpy.data.objects["isoRenderCamera"].data.type = 'ORTHO'
            bpy.data.objects["isoRenderCamera"].data.ortho_scale = bpy.context.scene.iso_cam_fov
        else:
            bpy.data.objects["isoRenderCamera"].data.type = 'PERSP'
            bpy.data.objects["isoRenderCamera"].data.lens = bpy.context.scene.iso_cam_fov
        bpy.data.objects["isoRenderCamera"].select_set(True)
        cam = bpy.context.active_object
        
        # base path for rendered images
        basePath = bpy.context.scene.iso_export_path + "/" + bpy.context.scene.iso_export_prefix
        
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
            
            # render as-is if requested
            if bpy.context.scene.iso_render_static:
                # render to image
                bpy.context.scene.camera = cam
                bpy.context.scene.render.filepath = basePath + str(i) + "_"
                bpy.ops.render.render(use_viewport=False, animation=False, write_still=True)
                continue

            # render each animation once per angle
            for t in obj.animation_data.nla_tracks:
                for s in t.strips:
                    if s.action.name in exportAnims:
                        obj.animation_data.action = s.action
                        for frame in range(bpy.context.scene.frame_end):
                            bpy.context.scene.frame_set(frame)
                
                            # render to image
                            bpy.context.scene.camera = cam
                            bpy.context.scene.render.filepath = basePath + s.action.name + "_" + str(i) + "f" + str(frame) + "_"
                            bpy.ops.render.render(use_viewport=False, animation=False, write_still=True)
        
        # delete lingering camera
        if bpy.context.scene.iso_delete_cam:
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
        row.prop(scene, "iso_export_path", text="Export Path")
        
        row = layout.row()
        row.prop(scene, "iso_export_prefix", text="Filename Prefix")
        
        layout.label(text="Comma-separated list of actions to render:")
        row = layout.row()
        row.prop(scene, "iso_action_names", text="Animations")
        
        row = layout.row()
        row.prop(scene, "iso_render_angles", text="Num Angles")
        row.prop(scene, "iso_angle_offset", text="Angle Offset")
        
        row = layout.row()
        row.prop(scene, "iso_camera_height", text="Cam Height")
        row.prop(scene, "iso_orbit_radius", text="Orbit Radius")
        
        row = layout.row()
        row.prop(scene, "iso_render_x", text="Render Width")
        row.prop(scene, "iso_render_y", text="Render Height")
        
        row = layout.row()
        row.prop(scene, "iso_filter_size", text="Filter Size")
        row.prop(scene, "iso_cam_fov", text="Camera Focal Length")
        
        row = layout.row()
        row.prop(scene, "iso_ortho_cam", text="Use Orthographic Camera")
        row.prop(scene, "iso_delete_cam", text="Cleanup camera")
        row.prop(scene, "iso_render_static", text="Disable Animation")
        
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
    
    bpy.types.Scene.iso_export_prefix = bpy.props.StringProperty(
        name = "Iso Export Prefix",
        subtype =  'FILE_NAME',
        default = "sprite"
    )
    
    bpy.types.Scene.iso_action_names = bpy.props.StringProperty(
        name = "Iso Action Names",
        subtype = 'NONE',
        default = ""
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
        default = 45
    )
    
    bpy.types.Scene.iso_orbit_radius = bpy.props.IntProperty(
        name = "Iso Orbit Radius",
        default = 70
    )
    
    bpy.types.Scene.iso_ortho_cam = bpy.props.BoolProperty(
        name = "Iso Ortho Camera",
        default = True
    )
    
    bpy.types.Scene.iso_delete_cam = bpy.props.BoolProperty(
        name = "Iso Delete Camera",
        default = True
    )
    
    bpy.types.Scene.iso_render_static = bpy.props.BoolProperty(
        name = "Iso Render Static",
        default = False
    )
    
    bpy.types.Scene.iso_render_x = bpy.props.IntProperty(
        name = "Iso Resolution X",
        default = 512
    )
    
    bpy.types.Scene.iso_render_y = bpy.props.IntProperty(
        name = "Iso Resolution Y",
        default = 512
    )
    
    bpy.types.Scene.iso_filter_size = bpy.props.FloatProperty(
        name = "Iso Filter Size",
        default = 1.5,
        min = 0.01,
        max = 100.0
    )
    
    bpy.types.Scene.iso_cam_fov = bpy.props.FloatProperty(
        name = "Iso Camera FOV",
        default = 7.31429,
        min = 0.01,
        max = 10000.0
    )
    
    bpy.utils.register_class(IsoRenderOperator)
    bpy.utils.register_class(IsoSpriteRender)


def unregister():
    del bpy.types.Scene.iso_export_path
    del bpy.types.Scene.iso_export_prefix
    del bpy.types.Scene.iso_action_names
    del bpy.types.Scene.iso_render_angles
    del bpy.types.Scene.iso_angle_offset
    del bpy.types.Scene.iso_camera_height
    del bpy.types.Scene.iso_orbit_radius
    del bpy.types.Scene.iso_ortho_cam
    del bpy.types.Scene.iso_delete_cam
    del bpy.types.Scene.iso_render_static
    del bpy.types.Scene.iso_render_x
    del bpy.types.Scene.iso_render_y
    del bpy.types.Scene.iso_filter_size
    del bpy.types.Scene.iso_cam_fov
    bpy.utils.unregister_class(IsoRenderOperator)
    bpy.utils.unregister_class(IsoSpriteRender)

if __name__ == "__main__":
    register()