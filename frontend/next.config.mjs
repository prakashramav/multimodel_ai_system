/** @type {import('next').NextConfig} */
const backendUrl = (
  process.env.BACKEND_URL || 
  process.env.NEXT_PUBLIC_BACKEND_URL || 
  'https://multimodel-ai-system-gen-ai.onrender.com'
).replace(/\/$/, '');

const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
