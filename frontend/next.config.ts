import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://35.208.254.175/:path*", 
      },
    ];
  },
};

export default nextConfig;