import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteStaticCopy } from "vite-plugin-static-copy";

export default defineConfig({
    plugins: [
        react(),
        viteStaticCopy({
            targets: [
                {
                    src: "node_modules/@ricky0123/vad-web/dist/vad.worklet.bundle.min.js",
                    dest: "",
                },
                {
                    src: "node_modules/@ricky0123/vad-web/dist/silero_vad_v6.onnx",
                    dest: "",
                },
                {
                    src: "node_modules/onnxruntime-web/dist/*.wasm",
                    dest: "",
                },
                {
                    src: "node_modules/onnxruntime-web/dist/*.mjs",
                    dest: "",
                },
            ],
        }),
    ],

    resolve: {
        alias: {
            "./Client": "./client",
        },
    },

    server: {
        proxy: {
            "/api": {
                target: "http://localhost:8000",
                changeOrigin: true,
            },
        },
    },
});