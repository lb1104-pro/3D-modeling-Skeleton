"""Run inside Blender 4.2+: blender -b --python blender_export.py -- motion.json character.glb

Produces animated rigid mesh parts, not a skinned or retargetable humanoid rig.
Uses only Blender's bundled Python. Does not require the app's dependencies.
"""
import argparse
import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('motion')
    parser.add_argument('output')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    data = json.loads(Path(args.motion).read_text(encoding='utf-8'))
    output = Path(args.output).resolve()
    if output.suffix.lower() != '.glb':
        raise ValueError('Output must have a .glb extension.')
    output.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.fps = int(data['metadata'].get('output_fps',24))
    scene.frame_start = 1
    scene.frame_end = len(data['frames'])
    blue = bpy.data.materials.new('Mannequin blue')
    blue.diffuse_color = (.17,.62,.75,1)
    gold = bpy.data.materials.new('Estimated center of mass')
    gold.diffuse_color = (1,.58,.15,1)
    def sphere(name,radius,material):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=radius)
        obj = bpy.context.object
        obj.name = name
        obj.data.materials.append(material)
        return obj
    def position(point):
        # Convert y-up to Blender z-up with a proper rotation (preserve handedness).
        return Vector((point[0],-point[2],point[1]))
    bones = []
    for a,b in data['edges']:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=1,depth=1)
        obj = bpy.context.object
        obj.name = data['joint_names'][a]+'__'+data['joint_names'][b]
        obj.rotation_mode = 'QUATERNION'
        obj.data.materials.append(blue)
        bones.append((obj,a,b))
    head = sphere('Head',.10,blue)
    view = data.get('export_view',{})
    markers = [sphere(name,.025,blue) for name in data['joint_names']] if view.get('show_joints',True) else []
    center = sphere('Estimated_CoM',.04,gold) if view.get('show_com',True) else None
    objects = [v[0] for v in bones]+[head]+markers+([center] if center else [])
    for frame,item in enumerate(data['frames'],1):
        points = item['joints']
        if points is None:
            # Zero scale exports reliably into glTF, unlike Blender visibility keys.
            for obj in objects:
                obj.scale = (0,0,0)
                obj.keyframe_insert('scale',frame=frame)
            continue
        points = [position(p) for p in points]
        for obj,a,b in bones:
            delta = points[b]-points[a]
            obj.location = (points[a]+points[b])/2
            obj.scale = (.035,.035,max(delta.length,.0001))
            obj.rotation_quaternion = delta.to_track_quat('Z','Y')
            for field in ('location','scale','rotation_quaternion'):
                obj.keyframe_insert(field,frame=frame)
        head.location = points[3]
        for obj,point in zip(markers,points):
            obj.location = point
        if center:
            center.location = position(item['center_of_mass'])
        for obj in [head]+markers+([center] if center else []):
            obj.scale = (1,1,1)
            obj.keyframe_insert('location',frame=frame)
            obj.keyframe_insert('scale',frame=frame)
    # Set linear interpolation where available; force sampling includes all frames.
    for obj in objects:
        action = obj.animation_data.action if obj.animation_data else None
        if action and hasattr(action,'fcurves'):
            for curve in action.fcurves:
                for key in curve.keyframe_points:
                    key.interpolation = 'LINEAR'
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(output.with_suffix('.blend')))
    bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',export_animations=True,
                             export_frame_range=True,export_force_sampling=True,
                             export_animation_mode='SCENE')
    print(f'Wrote {output} and {output.with_suffix(".blend")}')

if __name__ == '__main__':
    main()
