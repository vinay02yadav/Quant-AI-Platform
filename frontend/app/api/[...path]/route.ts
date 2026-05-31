import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  // Await the params before using them (Next.js App Router requirement)
  const resolvedParams = await params;
  const pathString = resolvedParams.path.join('/');
  
  // Combine your GCP IP with the requested path
  const backendUrl = `http://35.208.254.175:8000/${pathString}`;

  try {
    const response = await fetch(backendUrl, { cache: 'no-store' });
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to connect to Google Cloud backend' },
      { status: 500 }
    );
  }
}