module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#fff7ed", // fallback solid
        text: "#ef4444",       // stronger red
        primary: "#f97316",
        primaryHover: "#ea580c",
        accent: "#f9a8d4",
        border: "#fcd9bd",     // peach border
        gradientStart: "#ef4444",
        gradientMiddle: "#f97316",
        gradientEnd: "#9333ea",
      },
    },
  },
  plugins: [],
};
