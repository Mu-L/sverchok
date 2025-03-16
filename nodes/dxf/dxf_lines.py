import bpy
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, zip_long_repeat, dataCorrect_np
from ezdxf.math import Vec3
from mathutils import Vector
import ezdxf
from ezdxf import colors
from ezdxf import units
from ezdxf.tools.standards import setup_dimstyle
from sverchok.utils.dxf import LWdict, lineweights, linetypes



class DxfLines:
    def __repr__(self):
        return "<DXF Lines>"

    def __init__(self, vers, color, lineweight, metadata, linetype, node, color_int):
        self.vers = vers
        self.node = node
        self.color = color
        self.color_int = color_int
        self.lineweight = lineweight
        self.metadata = metadata
        self.linetype = linetype

    def draw(self):
        return self.vers


class SvDxfLinesNode(SverchCustomTreeNode, bpy.types.Node):
    bl_idname = 'SvDxfLinesNode'
    bl_label = 'DXF Lines'
    bl_icon = 'EXPORT'
    sv_icon = 'SV_PATH_SVG'
    bl_category = 'DXF'
    sv_dependencies = {'ezdxf'}

    scale: bpy.props.FloatProperty(default=1.0,name='scale')

    text_scale: bpy.props.FloatProperty(default=1.0,name='text_scale')

    metadata: bpy.props.StringProperty(default='',name='metadata')

    color_int: bpy.props.IntProperty(default=-4, min=-4, max=255,name='color', description='-4 is ignore, -3')

    unit_color: bpy.props.FloatVectorProperty(
        update=updateNode, name='', default=(.3, .3, .2, 1.0),
        size=4, min=0.0, max=1.0, subtype='COLOR'
    )

    linetype: bpy.props.EnumProperty(
        name="linetype", description="linetypes", default='CONTINUOUS', items=linetypes, update=updateNode)

    lineweight: bpy.props.EnumProperty(
        name="lineweight", description="lineweight", default='0.00', items=lineweights, update=updateNode)

    def sv_init(self, context):
        self.inputs.new('SvVerticesSocket', 'verts')
        self.inputs.new('SvStringsSocket', 'edges')
        self.inputs.new('SvColorSocket', 'color').custom_draw = 'draw_color_socket'
        self.inputs.new('SvTextSocket', 'metadata').prop_name='metadata'
        self.outputs.new('SvSvgSocket', 'dxf')

    def draw_buttons(self, context, layout):
        layout.prop(self, "linetype", expand=False)
        layout.prop(self, "lineweight", expand=False)
        layout.prop(self, "color_int", expand=False)

    def draw_color_socket(self, socket, context, layout):
        if not socket.is_linked:
            layout.prop(self, 'unit_color', text="")
        else:
            layout.label(text=socket.name+ '. ' + str(socket.objects_number))

    def process(self):
        if self.outputs['dxf'].is_linked:
            # All starts with dxf socket
            if self.inputs['verts'].is_linked:
                vers_ = self.inputs['verts'].sv_get()
            if self.inputs['edges'].is_linked:
                edges_ = self.inputs['edges'].sv_get()
            #if self.inputs['color'].is_linked:
            # color [[ (1,0,1) ]]
            if self.inputs['color'].is_linked:
                cols_ = self.inputs['color'].sv_get(deepcopy=False)
                cols_ = dataCorrect_np(cols_)[0][0]
            else:
                cols_ = self.unit_color[:]
            color_int = self.color_int
            #if self.inputs['metadata'].is_linked:
            # It is any text [['text']]
            meta_ = self.inputs['metadata'].sv_get()
            dxf = []
            # not match long repeate because we can use several nodes 
            # and multipliying mesh with colors absurdic, except meta
            # lw,lt - lineweight, linetype
            lw = LWdict[self.lineweight]
            lt = self.linetype
            for obv,obe,met in zip_long_repeat(vers_,edges_,meta_):
                for ed in obe:
                    points = []
                    for ver, me in zip_long_repeat(ed,met):
                        vr = obv[ver]
                        if type(vr) == Vector: vr = vr.to_tuple()
                        points.append(vr)
                    edgs = DxfLines(points,cols_,lw,me,lt,self,color_int)
                    dxf.append(edgs)
            self.outputs['dxf'].sv_set([dxf])

    def sv_update(self):
        if not ("verts" in self.inputs):
            return

def register():
    bpy.utils.register_class(SvDxfLinesNode)

def unregister():
    bpy.utils.unregister_class(SvDxfLinesNode)

if __name__ == "__main__":
    register()