import cil
from semantic import VariableInfo, Scope

class BaseCOOLToCILVisitor:
    def __init__(self, context):
        self.dottypes = []
        self.dotdata = [ cil.DataNode('_empty', '')]
        self.dotcode = []
        self.current_type = None
        self.current_method = None
        self.current_function = None
        self.context = context
        self.basic_types()
    
    @property
    def params(self):
        return self.current_function.params
    
    @property
    def localvars(self):
        return self.current_function.localvars
    
    @property
    def instructions(self):
        return self.current_function.instructions
    
    @property
    def labels(self):
        return self.current_function.labels

    def basic_types(self):
        for basicType in ['Int', 'String', 'Bool']:
            cil_type = self.register_type(basicType)
            cil_type.attributes.append(self.to_attribute_name('value', basicType))
        
            for method , typeMethod in self.context.get_type(basicType).all_methods():
                cil_type.methods.append((method.name, self.to_function_name(method.name, typeMethod.name)))


    def register_param(self, vinfo):
        vinfo.cilName = vinfo.name # f'param_{self.current_function.name[9:]}_{vinfo.name}_{len(self.params)}'
        param_node = cil.ParamNode(vinfo.cilName)
        self.params.append(param_node)
        return vinfo.cilName
    
    def register_local(self, vinfo):
        vinfo.cilName = f'local_{self.current_function.name[9:]}_{vinfo.name}_{len(self.localvars)}'
        local_node = cil.LocalNode(vinfo.cilName)
        self.localvars.append(local_node)
        return vinfo.cilName
    
    def register_label(self):
        name = f'label_{self.current_function.name[9:]}_{len(self.labels)}'
        self.labels.append(name)
        return name

    def define_internal_local(self):
        vinfo = VariableInfo('internal', None)
        return self.register_local(vinfo)

    def register_instruction(self, instruction):
        self.instructions.append(instruction)
        return instruction

    def to_function_name(self, method_name, type_name):
        return f'function_{method_name}_at_{type_name}'
    
    def to_attribute_name(self, attr_name, attr_type):
        return f'attribute_{attr_type}_{attr_name}'

    def register_function(self, function_name):
        function_node = cil.FunctionNode(function_name, [], [], [], [])
        self.dotcode.append(function_node)
        return function_node
    
    def register_type(self, name):
        type_node = cil.TypeNode(name)
        self.dottypes.append(type_node)
        return type_node

    def register_data(self, value):
        for dataNode in self.dotdata:
            if dataNode.value == value:
                return dataNode
    
        vname = f'data_{len(self.dotdata)}'
        data_node = cil.DataNode(vname, value)
        self.dotdata.append(data_node)
        return data_node


    def get_attr(self, function_name, attribute):
        for dottype in self.dottypes:
            if dottype.name == function_name:
                break

        for attrib in dottype.attributes:
            if attrib.split('_')[-1] == attribute:
                break

        return attrib

    def get_method(self, type_name, method_name):
        for typeContext in self.context.types:
            if typeContext == type_name:
                break

        for method, methodType in self.context.types[typeContext].all_methods():
            if method.name == method_name:
                break

        return self.to_function_name(method.name, methodType.name) 