#version 120
varying vec3 light_dir;
varying vec2 uv;

uniform sampler2D normal_map;

void main() {
    vec3 normal = texture2D(normal_map, uv).rgb * 2.0 - 1.0;
    normal = normalize(normal);
    float intensity = max(dot(normal, normalize(light_dir)), 0.0);
    gl_FragColor = vec4(vec3(intensity), 1.0);
}