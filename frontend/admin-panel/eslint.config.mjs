import js from '@eslint/js'
import prettier from 'eslint-config-prettier'
import vue from 'eslint-plugin-vue'
import globals from 'globals'
import ts from 'typescript-eslint'

export default ts.config(
  {
    ignores: ['node_modules/**', '.nuxt/**', '.output/**', 'dist/**', 'coverage/**'],
  },
  js.configs.recommended,
  ...ts.configs.recommended,
  ...vue.configs['flat/recommended'],
  {
    files: ['**/*.{js,mjs,ts,vue}'],
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
  },
  {
    files: ['**/*.vue'],
    languageOptions: { parserOptions: { parser: ts.parser } },
    rules: { 'vue/multi-word-component-names': 'off' },
  },
  {
    files: ['**/*.{ts,vue}'],
    // Nuxt supplies Vue and framework imports at build time. TypeScript checks names.
    rules: { 'no-undef': 'off' },
  },
  {
    files: ['components/ui/**/*.{ts,vue}'],
    // Imported UI primitives expose generic data and third-party slot contracts.
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      // Optional wrapper props must remain undefined for primitive defaults to apply.
      'vue/require-default-prop': 'off',
    },
  },
  {
    files: ['components/ui/chart/ChartSingleTooltip.vue'],
    // The tooltip factory mounts a supplied component into each chart overlay.
    rules: { 'vue/one-component-per-file': 'off' },
  },
  prettier,
)
