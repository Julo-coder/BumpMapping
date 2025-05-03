#version 120
attribute vec3 position;
attribute vec3 normal;
attribute vec3 tangent;
attribute vec3 bitangent;
attribute vec2 texcoord;

varying vec3 light_dir;
varying vec2 uv;

uniform mat4 modelview;
uniform mat4 projection;
uniform vec3 light_pos;

void main() {
    vec4 pos = modelview * vec4(position, 1.0);
    
    vec3 T = normalize(mat3(modelview) * tangent);
    vec3 B = normalize(mat3(modelview) * bitangent);
    vec3 N = normalize(mat3(modelview) * normal);
    mat3 TBN = mat3(T, B, N);
    
    vec3 light_pos_view = (modelview * vec4(light_pos, 1.0)).xyz;
    light_dir = TBN * (light_pos_view - pos.xyz);
    
    uv = texcoord;
    gl_Position = projection * pos;
}