// import { NextRequest, NextResponse } from 'next/server';

// export async function GET(
//   request: NextRequest,
//   { params }: { params: Promise<{ path: string[] }> }
// ) {
//   // Await the params before using them (Next.js App Router requirement)
//   const resolvedParams = await params;
//   const pathString = resolvedParams.path.join('/');
  
//   // Combine your GCP IP with the requested path
//   const backendUrl = `http://35.208.254.175:8000/${pathString}`;

//   try {
//     const response = await fetch(backendUrl, { cache: 'no-store' });
//     const data = await response.json();
//     return NextResponse.json(data);
//   } catch (error) {
//     return NextResponse.json(
//       { error: 'Failed to connect to Google Cloud backend' },
//       { status: 500 }
//     );
//   }
// }


import { NextRequest, NextResponse } from "next/server";

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const endpoint = params.path.join("/");
  
  // 🚀 CRITICAL FIX: We strip out port 8000 if it exists in your .env, 
  // forcing the connection to standard Port 80 where Docker is listening.
  let baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:80";
  baseUrl = baseUrl.replace(":8000", ""); 
  
  const backendUrl = `${baseUrl}/${endpoint}`;

  try {
    const response = await fetch(backendUrl, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Backend refused connection: ${response.status}`);
    }
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}