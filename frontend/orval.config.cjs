module.exports = {
    "cf1-backend": {
        input: "./openapi.json",
        output: {
            target: "./src/api/generated.ts",
            client: "swr",
            override: {
                mutator: {
                    path: "./src/api/axios.ts",
                    name: "customInstance"
                }
            }
        },
    },
};
