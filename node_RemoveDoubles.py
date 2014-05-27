import bmesh, mathutils
from mathutils import Vector, Matrix
from node_s import *
from util import *

# 
# Remove Doubles
# by Linus Yng

def remove_doubles(vertices, faces, d, find_doubles=False):
    if not faces or not vertices:
        return False
    
    if len(faces[0])==2:
        EdgeMode = True
    else:
        EdgeMode = False
                
    bm=bmesh.new() 
    bm_verts =[bm.verts.new(v) for v in vertices]
    if EdgeMode:
        for edge in faces:
            bm.edges.new([bm_verts[i] for i in edge])
    else:
        for face in faces:
            bm.faces.new([bm_verts[i] for i in face])
    
    
    if find_doubles:
        res = bmesh.ops.find_doubles(bm, verts=bm_verts, dist=d)
        res['targetmap']
        doubles=[vert.co[:] for vert in res['targetmap'].keys()]
    else:
        doubles = []
        
    bmesh.ops.remove_doubles(bm, verts=bm_verts, dist=d)    
    edges = []
    faces = []
    bm.verts.index_update()
    bm.edges.index_update()
    bm.faces.index_update()
    for edge in bm.edges[:]:
        edges.append([v.index for v in edge.verts[:]])
    verts = [vert.co[:] for vert in bm.verts[:]]
    for face in bm.faces:
        faces.append([v.index for v in face.verts[:]])
    bm.clear()
    bm.free()
    return (verts,edges,faces,doubles)


class SvRemoveDoublesNode(Node, SverchCustomTreeNode):
    '''Remove doubles'''
    bl_idname = 'SvRemoveDoublesNode'
    bl_label = 'Remove Doubles BETA'
    bl_icon = 'OUTLINER_OB_EMPTY'
    
    distance = bpy.props.FloatProperty(name='Distance', description='Remove distance', 
                                       default=0.001, precision=3, min=0, update=updateNode)

    def init(self, context):
        self.inputs.new('VerticesSocket', 'Vertices', 'Vertices')
        self.inputs.new('StringsSocket', 'PolyEdge', 'PolyEdge')
        
        self.outputs.new('VerticesSocket', 'Vertices', 'Vertices')
        self.outputs.new('StringsSocket', 'Edges', 'Edges')
        self.outputs.new('StringsSocket', 'Polygons', 'Polygons')
        self.outputs.new('VerticesSocket', 'Doubles', 'Doubles')
            
    def draw_buttons(self, context, layout):
        layout.prop(self,'distance',text="Distance")

    def update(self):
        if not any([s.links for s in self.outputs]):
            return
            
        if 'Vertices' in self.inputs and self.inputs['Vertices'].links and \
            'PolyEdge' in self.inputs and self.inputs['PolyEdge'].links:
                
            verts = Vector_generate(SvGetSocketAnyType(self,self.inputs['Vertices']))
            polys = SvGetSocketAnyType(self,self.inputs['PolyEdge'])
            if 'Doubles' in self.outputs:
                has_double_out = bool('Doubles' in self.outputs)
            verts_out = []
            edges_out = []
            polys_out = []
            d_out = []
                     
            for obj in zip(verts,polys):
                res = remove_doubles(obj[0], obj[1], self.distance, has_double_out)
                if not res:
                    return
                verts_out.append(res[0])
                edges_out.append(res[1])
                polys_out.append(res[2])
                d_out.append(res[3])
                
            if 'Vertices' in self.outputs and self.outputs['Vertices'].links:
                SvSetSocketAnyType(self, 'Vertices',verts_out)
            
            if 'Edges' in self.outputs and self.outputs['Edges'].links:
                SvSetSocketAnyType(self, 'Edges',edges_out) 
                
            if 'Polygons' in self.outputs and self.outputs['Polygons'].links:
                SvSetSocketAnyType(self, 'Polygons', polys_out) 
            
            if 'Doubles' in self.outputs and self.outputs['Doubles'].links:
                SvSetSocketAnyType(self, 'Doubles', d_out) 
            

    def update_socket(self, context):
        self.update()

def register():
    bpy.utils.register_class(SvRemoveDoublesNode)   
    
def unregister():
    bpy.utils.unregister_class(SvRemoveDoublesNode)

if __name__ == "__main__":
    register()







