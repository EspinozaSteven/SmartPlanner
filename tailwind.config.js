/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/*", "./node_modules/flowbite/**/*.js"],
  theme: {
    extend: {},
  },
  plugins: [require("flowbite/plugin")],
};
