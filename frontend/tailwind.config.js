/** @type {import('tailwindcss').Config} */
module.exports = {
  // NOTE: Update this to include the paths to all files that contain Nativewind classes.
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    colors:{
      primary: "#E5E2E1",
      secondary: "#D1C6AB",
      gold:"#EDC200",
      bgPrimary:"#1C1B1B",
      bgSecondary:"#2A2A2A",
      horde:"#8C1616",
      alliance:"#004A94"
    },
    extend: {},
  },
  plugins: [],
}