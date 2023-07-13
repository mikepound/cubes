import bpy
import os
import math
import numpy as np

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
	'name' : 'PolycubeVisualizer',
	'author' : 'dshot92',
	'description' : '3D Visualization of "https://github.com/mikepound/cubes".',
	'blender' : (3, 5, 0),
	'version' : (0, 1, 0),
	'location' : '',
	'warning' : '',
	'category' : 'Polycubes'
}


def clear_scene():
	bpy.ops.object.select_all(action = 'SELECT')
	bpy.ops.object.delete(use_global=True, confirm=False)
	# Delete all objects in the scene
	for collection in bpy.data.collections:
		for obj in collection.objects:
			bpy.data.objects.remove(obj, do_unlink=True)
		# Remove the collection
		bpy.data.collections.remove(collection)

	for image in bpy.data.images:
		image.use_fake_user = False

	for mat in bpy.data.materials:
		mat.use_fake_user = False

	# Recursively delete all data-blocks
	bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

	# Set Color to random for each object
	bpy.context.space_data.shading.color_type = 'RANDOM'


def read_shapes(path):
	if os.path.exists(path):
		return np.load(path, allow_pickle=True)

def apply_geometry_nodes_modifier(obj):

	# Create a new geometry nodes modifier
	modifier = obj.modifiers.new(name='Geometry Nodes', type='NODES')

	# Set up the node tree for the modifier
	node_group = bpy.data.node_groups.new('Polycubes', 'GeometryNodeTree')
	modifier.node_group = node_group

	# Create a Node Group Input node
	input_node = node_group.nodes.new(type='NodeGroupInput')
	node_group.inputs.new('NodeSocketGeometry', 'GeometryIn')
	input_node.location = (-400, 0)

	# Create a Node Group Output node
	output_node = node_group.nodes.new(type='NodeGroupOutput')
	node_group.outputs.new('NodeSocketGeometry', 'GeometryOut')
	output_node.location = (0, 0)
	# Cube Node
	node_cube = node_group.nodes.new('GeometryNodeMeshCube')
	node_cube.location = (-400, -150)
	node_cube.inputs[0].default_value = (0.95, 0.95, 0.95)

	# Instance on Points Node
	node_instance = node_group.nodes.new('GeometryNodeInstanceOnPoints')
	node_instance.location = (-200, 0)

	# Create Links between nodes
	node_group.links.new(input_node.outputs[0],node_instance.inputs['Points'])
	node_group.links.new(node_cube.outputs['Mesh'],node_instance.inputs['Instance'])
	node_group.links.new(node_instance.outputs['Instances'],output_node.inputs[0])

	return modifier

def create_shapes(shapes):

	n = len(shapes)
	dim = max(max(a.shape) for a in shapes)
	i = math.isqrt(n) + 1
	pad = 1
	modifier = None

	for idx, shape in enumerate(shapes):
		x = (idx % i) * dim + (idx % i)
		y = (idx // i) * dim + (idx // i)
		xpad = x * pad
		ypad = y * pad
		s = shape.shape

		verts = []
		for xi in range(s[0]):
			for yi in range(s[1]):
				for zi in range(s[2]):
					if shape[xi, yi, zi] == 1:
						verts.append((xpad + xi, ypad + yi, zi))

		mesh = bpy.data.meshes.new(name=f'ShapeMesh_{idx}')
		mesh.from_pydata(verts, [], [])
		obj = bpy.data.objects.new(name=f'ShapeObject_{idx}', object_data=mesh)
		obj.location = (xpad + s[0] // 2, ypad + s[1] // 2, s[2] // 2)
		bpy.context.collection.objects.link(obj)

		# Set origin to object median
		bpy.ops.object.select_all(action='SELECT')
		bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

def poly_apply_modifier():
	temp_mesh = bpy.data.meshes.new('emptyMesh')
	temp_obj = bpy.data.objects.new(name=f'empy_mod', object_data=temp_mesh)
	bpy.context.scene.collection.objects.link(temp_obj)

	modifier = apply_geometry_nodes_modifier(temp_obj)
	for obj in bpy.data.objects:
		mod = obj.modifiers.new(modifier.name, 'NODES')
		mod.node_group = modifier.node_group

	# Delete temp object
	bpy.ops.object.select_all(action='DESELECT')
	bpy.data.objects[temp_obj.name].select_set(True)
	bpy.ops.object.delete()


class Load_NPY_Operator(bpy.types.Operator):
	bl_idname = 'polycubes.load_npy'
	bl_label = 'Load_NPY'
	bl_description = 'Load NPY file cache'

	def execute(self, context):

		npy_file = bpy.path.abspath(bpy.context.scene.Load_NPY_Props.npy_file)
		if npy_file == '':
			self.report({'WARNING'}, 'No File Selected')
			return {'FINISHED'}

		clear_scene()
		shapes = read_shapes(npy_file)
		create_shapes(shapes)
		poly_apply_modifier()

		collection_name = f'{npy_file.split(os.sep)[-1]}'
		scene_collection = bpy.context.scene.collection
		coll_poly = bpy.data.collections.new(name=collection_name)
		scene_collection.children.link(coll_poly)
		for obj in bpy.data.objects:
			coll_poly.objects.link(obj)
			scene_collection.objects.unlink(obj)

		print("\n")
		self.report({'INFO'}, f'Loaded {len(shapes)} Polycubes')
		return {'FINISHED'}

class Load_NPY_Panel(bpy.types.Panel):

	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_label = 'Polycubes Visualizer'
	bl_category = 'Polycubes'

	def draw(self, context):
		layout = self.layout
		props = context.scene.Load_NPY_Props
		box = layout.box()

		box.label(text='Select NPY file to load')
		box.prop(props, 'npy_file', text='',)
		box.operator(
			'polycubes.load_npy',
			text='Load NPY cache',
		)

class Load_NPY_Props(bpy.types.PropertyGroup):
	npy_file: bpy.props.StringProperty(
		name='npy_file',
		subtype='FILE_PATH',
	)


classes = (
	Load_NPY_Operator,
	Load_NPY_Panel,
	Load_NPY_Props,
)

def register():
	for bl_class in classes:
		bpy.utils.register_class(bl_class)
	bpy.types.Scene.Load_NPY_Props = bpy.props.PointerProperty(type=Load_NPY_Props)

def unregister():
	for bl_class in reversed(classes):
		bpy.utils.unregister_class(bl_class)
	del bpy.types.Scene.RDBE_Props