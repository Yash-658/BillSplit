/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        cream: "#f7f8fb",
        coral: "#f26b5b",
        mint: "#dff4ec",
      },
      boxShadow: {
        soft: "0 20px 60px rgba(32, 47, 78, 0.08)",
      },
    },
  },
  plugins: [],
};
