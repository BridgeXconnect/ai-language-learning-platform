/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_V0_API_KEY: process.env.V0_API_KEY,
    NEXT_PUBLIC_V0_PROJECT_ID: process.env.V0_PROJECT_ID,
    NEXT_PUBLIC_V0_BASE_URL: process.env.V0_BASE_URL,
    NEXT_PUBLIC_V0_WS_URL: process.env.V0_WS_URL,
  },
}

export default nextConfig
