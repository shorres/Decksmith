const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const webpack = require('webpack');

module.exports = {
  mode: process.env.NODE_ENV || 'development',
  
  entry: {
    app: './src/renderer/app.ts',
    preload: './src/renderer/preload.ts'
  },
  
  output: {
    path: path.resolve(__dirname, 'dist/renderer'),
    filename: '[name].js',
    clean: true,
    globalObject: 'this'
  },
  
  target: 'electron-renderer',
  
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader']
      },
      {
        test: /\.(png|jpg|jpeg|gif|svg|ico)$/,
        type: 'asset/resource'
      }
    ]
  },
  
  resolve: {
    extensions: ['.ts', '.js']
  },
  
  plugins: [
    new HtmlWebpackPlugin({
      template: './src/renderer/index.html',
      filename: 'index.html',
      chunks: ['app']
    }),
    new MiniCssExtractPlugin({
      filename: '[name].css'
    }),
    new webpack.ProvidePlugin({
      global: ['global', 'default']
    })
  ],
  
  devServer: {
    static: {
      directory: path.join(__dirname, 'dist/renderer')
    },
    port: 8080,
    hot: true
  },
  
  devtool: process.env.NODE_ENV === 'development' ? 'source-map' : false
};
