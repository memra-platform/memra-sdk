/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    MEMRA_API_URL: process.env.MEMRA_API_URL || 'https://api.memra.co',
  },
}

module.exports = nextConfig 