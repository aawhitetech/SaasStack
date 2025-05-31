import type { NextConfig } from "next";

const nextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/api-django/:path*/',
        destination: 'http://127.0.0.1:8000/:path*/',
      },
    ]
  },
  trailingSlash: true,
};

export default nextConfig;
