from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, optimize_loop_structure, texture_stride, texture_shape
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.operators.scalar_pow import ScalarPow

template = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, X0)%%;

%%UNIFORM(vec2, s_y)%%;
%%UNIFORM(vec4, d_Y)%%;
%%UNIFORM(vec4, s_Y)%%;

%%UNIFORM(vec2, d_x0)%%;
%%UNIFORM(vec2, s_x0)%%;
%%UNIFORM(vec4, d_X0)%%;
%%UNIFORM(vec4, s_X0)%%;

%%UNIFORM(float, value)%%;

void main() {
    vec4 p_Y = convert_position(gl_FragCoord.xy, s_y, s_Y, d_Y);    
    vec4 p_X0 = mod(p_Y, d_X0); // for broadcasting
    vec2 p_x0 = convert_position(p_X0, s_X0, s_x0, d_x0);

    vec4 x0 = texture2D(X0, p_x0 / d_x0);
    vec4 y;
    
    y = pow(x0, value);
    
    gl_FragColor = y;
}
"""


@WebGLDescriptorGenerator.register_handler(ScalarPow)
def elementwise_add(op: ScalarPow, _: MemoryLayout) -> List[Kernel]:
    x0 = op.inputs["x0"]
    y = op.outputs["y"]

    shapes, strides = optimize_loop_structure([x0, y], y)

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "X0": x0,

        "s_y": texture_stride(y),
        "d_Y": shapes[y],
        "s_Y": strides[y],

        "d_x0": texture_shape(x0),
        "s_x0": texture_stride(x0),
        "d_X0": shapes[x0],
        "s_X0": strides[x0],

        "value": op.parameters["value"],
    })

    source = template
    source = name_injector.inject(source)
    source = uniform_injector.inject(source)

    kernel = Kernel(
        source,
        name_injector.name,
        uniform_injector.samplers,
        uniform_injector.uniforms,
        y
    )

    return [kernel]
