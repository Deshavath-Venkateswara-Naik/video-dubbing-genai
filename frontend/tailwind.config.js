/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#6366f1',
                    hover: '#4f46e5',
                },
                bg: {
                    dark: '#0f172a',
                    card: 'rgba(30, 41, 59, 0.7)',
                },
                text: {
                    main: '#f8fafc',
                    muted: '#94a3b8',
                }
            },
            backdropBlur: {
                xs: '2px',
            },
            animation: {
                'slow-spin': 'spin 3s linear infinite',
            }
        },
    },
    plugins: [],
}
