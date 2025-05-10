#version 120

varying vec3 light_dir;
varying vec2 uv;

uniform sampler2D normal_map;

void main() {
    // Get the normal from the normal map
    vec3 normal = texture2D(normal_map, uv).rgb * 2.0 - 1.0;
    normal = normalize(normal);
    
    // Calculate basic lighting with ambient
    float ambient = 0.3;  // Add ambient light
    float diffuse = max(dot(normal, normalize(light_dir)), 0.0);
    float lighting = ambient + diffuse;
    
    // Sample texture color and apply lighting
    vec4 texColor = texture2D(normal_map, uv);
    gl_FragColor = vec4(texColor.rgb * lighting, 1.0);
}