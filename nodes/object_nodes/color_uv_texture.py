# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
import numpy as np
from bpy.props import BoolProperty, StringProperty, FloatVectorProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import (updateNode, second_as_first_cycle as safc)


class SvMeshUVColorNode(SverchCustomTreeNode, bpy.types.Node):
    ''' Find pixel on UV texture from mesh object and change its color'''
    bl_idname = 'SvMeshUVColorNode'
    bl_label = 'Set UV Color'
    bl_icon = 'UV_DATA'
    is_output = True
    is_scene_dependent = True
    is_animation_dependent = True

    image: StringProperty(default='', update=updateNode)
    unit_color: FloatVectorProperty(name='', default=(1.0, 1.0, 1.0, 1.0),
        size=4, min=0.0, max=1.0, subtype='COLOR', update=updateNode)

    def sv_draw_buttons(self, context,   layout):
        ob = self.inputs[0].sv_get(default=[[]])[0]
        if ob and ob.type == 'MESH':
            layout.prop_search(self, 'image', bpy.data, "images", text="")

    def sv_init(self, context):
        si = self.inputs.new
        si('SvObjectSocket', 'Mesh Object')
        si('SvVerticesSocket', 'Point on mesh')
        color_socket = si('SvColorSocket', 'Color on UV')
        color_socket.prop_name = 'unit_color'

    def process(self):
        Object, Points, Colors = self.inputs
        dps = bpy.context.evaluated_depsgraph_get()
        obj = Object.sv_get()[0]  # triangulate faces
        bvh = BVHTree.FromObject(obj, dps)
        point = Points.sv_get()[0]
        color = Colors.sv_get()[0]
        ran = range(3)
        image = bpy.data.images[self.image]
        width, height = image.size
        uvMap = obj.data.uv_layers[0].data
        pixels = np.array(image.pixels[:]).reshape(width,height,4)
        for P, C in zip(point, safc(point, color)):
            loc, norm, ind, dist = bvh.find_nearest(P)
            found_poly = obj.data.polygons[ind]
            verticesIndices = found_poly.vertices
            p1, p2, p3 = [obj.data.vertices[verticesIndices[i]].co for i in ran]
            uvMapIndices = found_poly.loop_indices
            uv1, uv2, uv3 = [uvMap[uvMapIndices[i]].uv.to_3d() for i in ran]
            V = barycentric_transform(loc, p1, p2, p3, uv1, uv2, uv3)
            Vx, Vy = int(V.x*(width-1)), int(V.y*(height-1))
            pixels[Vy, Vx] = C
        image.pixels = pixels.flatten().tolist()


def register():
    bpy.utils.register_class(SvMeshUVColorNode)


def unregister():
    bpy.utils.unregister_class(SvMeshUVColorNode)
