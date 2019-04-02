const path = require('path');

module.exports = {
    entry: {
        base: './ngo_explorer/static/js_src/base.js',
        data: './ngo_explorer/static/js_src/data.js',
        home: './ngo_explorer/static/js_src/home.js',
        upload: './ngo_explorer/static/js_src/upload.js',
    },
    mode: 'development',
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'ngo_explorer/static/js/')
    },
    module: {
        rules: [
            {
                test: /\.m?js$/,
                exclude: /(node_modules|bower_components)/,
                use: {
                    loader: 'babel-loader',
                }
            }
        ]
    }
};