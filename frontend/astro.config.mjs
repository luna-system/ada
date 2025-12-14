import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  devServer: {
    proxy: {
      '/api': 'http://localhost:7000'
    }
  }
});
