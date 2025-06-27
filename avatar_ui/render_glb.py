# import numpy as np
# import trimesh
# import pyrender
# from PIL import Image
# import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument("--input", type=str, required=True)
# parser.add_argument("--output", type=str, required=True)
# args = parser.parse_args()

# # Load GLB as a scene
# scene_or_mesh = trimesh.load(args.input, force='scene')

# # Apply rotation to align the face upright and facing camera
# rotation = trimesh.transformations.euler_matrix(
#     np.radians(-90),  # rotate X -90° to make it upright
#     np.radians(180),  # rotate Y 180° to face camera
#     np.radians(180),    # Z 0° (keep level)
#     'rxyz'
# )

# # Create a pyrender scene
# scene = pyrender.Scene()

# # Add all meshes with transform
# for name, geom in scene_or_mesh.geometry.items():
#     geom.apply_transform(rotation)
#     mesh = pyrender.Mesh.from_trimesh(geom, smooth=False)
#     scene.add(mesh)

# # Add a camera directly in front of the face
# camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
# camera_pose = np.array([
#     [1.0, 0.0,  0.0,  0.0],
#     [0.0, 1.0,  0.0,  0.0],
#     [0.0, 0.0,  1.0,  5.0],  # Z=+2.0 units in front of face
#     [0.0, 0.0,  0.0,  1.0]
# ])
# scene.add(camera, pose=camera_pose)

# # Add light from camera direction
# light = pyrender.DirectionalLight(color=np.ones(3), intensity=3.0)
# scene.add(light, pose=camera_pose)

# # Render
# renderer = pyrender.OffscreenRenderer(viewport_width=512, viewport_height=512)
# color, _ = renderer.render(scene)
# renderer.delete()

# # Save
# Image.fromarray(color).save(args.output)
# print(f"✅ Saved front-facing image to: {args.output}")

import os
import argparse
import numpy as np
import trimesh
import pyrender
from PIL import Image
import math

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, required=True, help='Path to .glb file')
parser.add_argument('--output', type=str, required=True, help='Path to output .png file')
args = parser.parse_args()

# Load the GLB file
print(f"[INFO] Loading mesh from: {args.input}")
scene_or_mesh = trimesh.load(args.input, force='scene')

# Create Pyrender scene
scene = pyrender.Scene()

# Add all geometries from scene
if isinstance(scene_or_mesh, trimesh.Scene):
    for name, geom in scene_or_mesh.geometry.items():
        # 👉 Step 1: Rotate around Y to face the camera
        rot_y = trimesh.transformations.rotation_matrix(
            math.radians(180), [0, 1, 0], point=geom.bounds.mean(axis=0)
        )
        geom.apply_transform(rot_y)

        # 👉 Step 2: Rotate around Z to fix upside-down
        rot_z = trimesh.transformations.rotation_matrix(
            math.radians(180), [0, 0, 1], point=geom.bounds.mean(axis=0)
        )
        geom.apply_transform(rot_z)

        mesh = pyrender.Mesh.from_trimesh(geom, smooth=False)
        scene.add(mesh)

elif isinstance(scene_or_mesh, trimesh.Trimesh):
    rot_y = trimesh.transformations.rotation_matrix(
        math.radians(180), [0, 1, 0], point=scene_or_mesh.bounds.mean(axis=0)
    )
    scene_or_mesh.apply_transform(rot_y)

    rot_z = trimesh.transformations.rotation_matrix(
        math.radians(180), [0, 0, 1], point=scene_or_mesh.bounds.mean(axis=0)
    )
    scene_or_mesh.apply_transform(rot_z)

    mesh = pyrender.Mesh.from_trimesh(scene_or_mesh, smooth=False)
    scene.add(mesh)
# Add a camera
camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
cam_node = scene.add(camera, pose=np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 4.5],  # move camera back to see full face
    [0, 0, 0, 1],
]))

light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=7.0)
light_pose = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 4.5],  # move camera back to see full face
    [0, 0, 0, 1]
])
scene.add(light, pose=light_pose)

# Render the scene
renderer = pyrender.OffscreenRenderer(viewport_width=512, viewport_height=512)
color, _ = renderer.render(scene)
renderer.delete()

# Save the image
image = Image.fromarray(color)
image.save(args.output)
print(f"[✅] Rendered front face saved to: {args.output}")

