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
    // Transform vertex position
    vec4 pos = modelview * vec4(position, 1.0);
    gl_Position = projection * pos;
    
    // Calculate TBN matrix for normal mapping
    mat3 TBN = mat3(tangent, bitangent, normal);
    
    // Transform light direction to tangent space
    vec3 light_direction = normalize(light_pos - position);
    light_dir = TBN * light_direction;
    
    // Pass texture coordinates
    uv = texcoord;
}