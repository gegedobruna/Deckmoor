const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  publicPath: '/Deckmoor/',
  transpileDependencies: true,
  configureWebpack: {
    resolve: {
      extensions: ['.js', '.vue', '.json']
    }
  }
});
